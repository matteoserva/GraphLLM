import json
import queue
import select
import socket
import tempfile
import traceback
from threading import Thread

import yaml
from modules.clients import get_client_config, Client
from modules.graph import GraphExecutor, GraphException
from modules.graph.json_parser import JsonParser
from modules.logging.logger import Logger
from websockets.frames import Opcode
from websockets.server import ServerProtocol


class WebExec():
    def __init__(self,send,blob):
        self.blob = blob
        self.t = None
        self.send_chunk = send
        logger = Logger(verbose=True, web_logger=False)


        parameters = {}
        parameters["repeat_penalty"] = 1.0
        parameters["penalize_nl"] = False
        parameters["seed"] = -1


        self.executor_config = {"client":None, "client_parameters":parameters,"logger":logger}


        self.logger = logger
        self.keep_running = False

    def event(self,t,a,v):
        #print(t,a,v)

        res = {"type": t, "data":a}
        if t == "audio":
            binary_data = a[-1]
            text_data = a[:-1]
            data_index = self.blob.add_binary_data(binary_data)
            res = {"type": t, "data": text_data, "address":data_index}
            resp = json.dumps(res)
            encoded = resp
            el = self.send_chunk(encoded,True)
            pass
        else:
            resp = json.dumps(res)
            encoded = resp
            self.send_chunk(encoded)

    def _run(self,args):
        self.logger.addListener(self)
        self.logger.log("start")
        last_error = None
        try:
            client_config = get_client_config()
            client = Client.make_client(client_config)
            client.connect()
            self.executor_config["client"] = client
            self.executor = GraphExecutor(self.executor_config)
            self.executor.load_config(args)
            self.executor([])
        except GraphException as e:
            if isinstance(e.saved_i,BrokenPipeError):
                print("client disconnected")
            else:
                last_error = e.saved_i
        except BrokenPipeError:
            print("client disconnected")
        except Exception as e:
            last_error = e

        try:
            if last_error:
                traceback.print_exception(type(last_error), last_error, last_error.__traceback__)
                self.logger.log("error",str(last_error))

            self.logger.log("stop")

        except Exception as e:
            print("stop exception:",e)
            pass
        finally:
            self.logger.poison()
            self.logger.deleteListeners()

    def run(self,filename):
        self._run([filename])

_queue_sentinel = object()
class ExecHandler():
    def __init__(self,server,blob = None):
        self.blob = blob
        self.server = server
        self.protocol = ServerProtocol()
        self.socket = server.request
        self.alive = False
        self.received_events = queue.Queue()

    def _receive_thread(self):
        keep_running = True
        while keep_running:
            try:
                data = self.server.request.recv(65536)
            except OSError:  # socket closed
                data = b""
                

            if data:
                self.protocol.receive_data(data)
            else:
                self.protocol.receive_eof()
                self.alive = False
                keep_running = False
            
            for el in self.protocol.events_received():
                if el.opcode == Opcode.CLOSE:

                    self.alive = False
                    keep_running = False
                else:
                    self.received_events.put(el)
        self.received_events.put(_queue_sentinel)
    
    def _get_next_event(self):
        event = self.received_events.get()
        if event is _queue_sentinel:
            self.received_events.put(event)
            raise BrokenPipeError("connection closed in RX")
        return event

    def _send_queued_data(self):

        try:
            for data in self.protocol.data_to_send():
                if data:
                    self.server.wfile.write(data)
                else:

                    self.alive = False
                    break
        except:
            self.alive = False
            raise

    def _send_close(self):

        if self.alive:
            self.protocol.send_close()
        self._send_queued_data()
        self.alive = False

    def _send_text(self,text, synchronous = False):
        
        if self.alive:
            self.protocol.send_text(text.encode())
            self._send_queued_data()
        if not self.alive:
            raise BrokenPipeError("connection closed")
        if synchronous:
            return self._get_next_event()

    def _handshake(self):
        headers = self.server.headers.items()
        headers = [i + ": " + v for i, v in headers]
        headers = "\r\n".join(headers) + "\r\n\r\n"
        request = self.server.requestline + "\r\n" + str(headers)

        self.protocol.receive_data(request.encode())
        request = self.protocol.events_received()[0]
        response = self.protocol.accept(request)
        self.protocol.send_response(response)
        self.alive = True
        self._send_queued_data()

    def exec(self):
        self.state = 1
        self._handshake()
        
        try:
            rx_thread = Thread(target = self._receive_thread)
            rx_thread.start()
            event = self._get_next_event()
            json_graph = event.data.decode()
           
            with open(tempfile.gettempdir() + "/graph.json", "w") as f:
                a = json.loads(json_graph)
                f.write(json.dumps(a, indent=4))
            parser = JsonParser()
            parsed = parser.load(tempfile.gettempdir() + "/graph.json")
            with open(tempfile.gettempdir() + "/graph.yaml", "w") as f:
                f.write(yaml.dump(parsed, sort_keys=False))
            e = WebExec(self._send_text,self.blob)
            e.run(tempfile.gettempdir() + "/graph.yaml")
            self._send_close()
        finally:
            try:
                self.socket.shutdown(socket.SHUT_RD)
                self.socket.shutdown(socket.SHUT_WR)
            except:
                pass
            rx_thread.join()
            
            self.server.close_connection = True
        pass
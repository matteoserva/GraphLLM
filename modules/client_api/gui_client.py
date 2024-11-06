import queue
import json
import uuid

from threading import Lock, Event

class GuiClientAPI:
    _queue_sentinel = object()

    def __init__(self, send_handler,blob):
        self.received_events = queue.Queue()
        self.send_handler = send_handler
        self.blob = blob
        self.alive = True
        self.pending_requests = {}
        self.requests_lock = Lock()

    def _get_next_event(self):
        event = self.received_events.get()
        if event is self._queue_sentinel:
            self.received_events.put(event)
            raise BrokenPipeError("connection closed in RX")
        return event

    def _send_text(self, text, synchronous=False):

        self.send_handler._send_text(text)
        if synchronous:
            return self._get_next_event()

    def _remote_call(self,data):
        myuuid = str(uuid.uuid4())
        res = {"type": "request","id":myuuid}
        combined = {**res, **data}
        resp = json.dumps(combined)
        encoded = resp
        ev = Event()
        resp = {}
        with self.requests_lock:
           self.send_handler._send_text(encoded)
           self.pending_requests[myuuid] = (ev,resp)
        ev.wait()
        pass

    def node_print(self, node_name, *args, **kwargs):
        data = [node_name] + list(args)
        t = {"type":"print", "data":data}
        text = json.dumps(t)
        self._send_text(text)

    def play_audio(self,audio_data):
        binary_data = audio_data

        data_index = self.blob.add_binary_data(binary_data)
        res = { "subtype": "audio", "data": [], "address":data_index}
        self._remote_call(res)


    def rpc_call(self,node_name,function_name, function_args):
        myuuid = str(uuid.uuid4())
        data = [node_name] + [function_name] + list(function_args)
        res = {"type": "call", "id":myuuid, "data": data}
        resp = json.dumps(res)
        encoded = resp
        el = self._send_text(encoded)

# network api
    def notify_client_event(self, event):
        is_response = False
        if event.opcode == 1:
            json_val = json.loads(event.data)
            if json_val.get("type","") == "response":
                is_response = True
        if is_response:
            with self.requests_lock:
                ev, resp = self.pending_requests[json_val["id"]]
                resp["response"] = json_val
                ev.set()
                del self.pending_requests[json_val["id"]]
        else:
            self.received_events.put(event)

    def notify_client_close(self):
        self.received_events.put(self._queue_sentinel)
        with self.requests_lock:
            for el in self.pending_requests:
                ev,resp = self.pending_requests[el]
                ev.set()
            self.pending_requests = None


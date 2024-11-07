import queue
import json
import uuid

from threading import Lock, Event

class RequestsTracker:
    
    def __init__(self):
        self.pending_requests = {}
        self.requests_lock = Lock()
        
    def send_request(self,request_data, send_cb):
        myuuid = str(uuid.uuid4())
        res = {"type": "request","id":myuuid}
        combined = {**res, **request_data}
        resp = json.dumps(combined)
        encoded = resp
        ev = Event()
        resp = {}
        with self.requests_lock:
           self.pending_requests[myuuid] = (ev,resp)
        try:
            send_cb(encoded)
            ev.wait()            
        finally:
           with self.requests_lock:
               del self.pending_requests[myuuid]
        
        return resp["response"]
    
    def set_response(self,response_id, response_data):
        ev, resp = self.pending_requests.get(response_id,(None,None))
        if ev:
            resp["response"] = response_data
            ev.set()
        
        
    def destroy(self):
        with self.requests_lock:
            for el in self.pending_requests:
                self.set_response(el,None)
            self.pending_requests = None
    

class GuiClientAPI:
    _queue_sentinel = object()

    def __init__(self, send_handler,blob):
        self.received_events = queue.Queue()
        self.send_handler = send_handler
        self.blob = blob
        self.alive = True
        self.requests_tracker = RequestsTracker()

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
        res = self.requests_tracker.send_request(data,self.send_handler._send_text)
        return res

    def node_print(self, node_name, *args, **kwargs):
        data = [node_name] + list(args)
        t = {"type":"print", "data":data}
        text = json.dumps(t)
        print(*args, **kwargs)
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
            self.requests_tracker.set_response(json_val["id"],json_val)
        else:
            self.received_events.put(event)

    def notify_client_close(self):
        self.received_events.put(self._queue_sentinel)
        self.requests_tracker.destroy()


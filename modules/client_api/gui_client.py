import queue
import json
import uuid

class GuiClientAPI:
    _queue_sentinel = object()

    def __init__(self, send_handler,blob):
        self.received_events = queue.Queue()
        self.send_handler = send_handler
        self.blob = blob

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

    def node_print(self, node_name, *args, **kwargs):
        data = [node_name] + list(args)
        t = {"type":"print", "data":data}
        text = json.dumps(t)
        self._send_text(text)

    def play_audio(self,audio_data):
        binary_data = audio_data
        myuuid = str(uuid.uuid4())
        data_index = self.blob.add_binary_data(binary_data)
        res = {"type": "request", "subtype": "audio", "id":myuuid, "data": [], "address":data_index}
        resp = json.dumps(res)
        encoded = resp
        el = self._send_text(encoded,True)

    def rpc_call(self,node_name,function_name, function_args):
        myuuid = str(uuid.uuid4())
        data = [node_name] + [function_name] + list(function_args)
        res = {"type": "call", "id":myuuid, "data": data}
        resp = json.dumps(res)
        encoded = resp
        el = self._send_text(encoded)

# network api
    def notify_client_event(self, event):
        self.received_events.put(event)

    def notify_client_close(self):
        self.received_events.put(self._queue_sentinel)


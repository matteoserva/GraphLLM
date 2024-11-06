import queue

class GuiClientAPI:
    _queue_sentinel = object()

    def __init__(self, send_handler):
        self.received_events = queue.Queue()
        self.send_handler = send_handler

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

    def notify_client_event(self, event):
        self.received_events.put(event)

    def notify_client_close(self):
        self.received_events.put(self._queue_sentinel)
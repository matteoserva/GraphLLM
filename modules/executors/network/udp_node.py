from modules.executors.common import GenericExecutor
import socket
import select


class UDPSenderNode(GenericExecutor):
    node_type = "udp_sender"

    def __init__(self, node_graph_parameters):
        self.sock = None

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.address = conf["ip"]
        self.port = conf["port"]


    def __call__(self, prompt_args):
        if not self.sock:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.sock.settimeout(1.0)

        message = prompt_args[0] if prompt_args else ""
        addr = (self.address, self.port)
        self.sock.sendto(message.encode(), addr)
        return []

    def graph_started(self):
        pass

    def graph_stopped(self):
        if self.sock:
            self.sock.close()
            self.sock = None

    def setup_complete(self, *args, **kwargs):
        pass


class UDPReceiverNode(GenericExecutor):
    node_type = "udp_receiver"

    def __init__(self, node_graph_parameters):
        self.sock = None
        self.buffer_size = 4096

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.address = conf["ip"]
        self.port = conf["port"]
        self.free_runs = conf["free_runs"]
        if self.free_runs > 1:
            self.properties["free_runs"] = self.free_runs - 1


    def __call__(self, prompt_args):
        data, addr = self.sock.recvfrom(self.buffer_size)
        last_data = data.decode()
        if self.free_runs == 0:
            self.properties["free_runs"] = 1
        return [last_data]

    def graph_started(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((self.address, self.port))
        self.sock.setblocking(1)

    def graph_stopped(self):
        if self.sock:
            try:
                self.sock.shutdown(socket.SHUT_RDWR)
            except OSError as e:
                if e.errno == 107:
                    # Error is, "Transport endpoint is not connected".
                    # We don't care.
                    pass
                else:
                    raise e
            self.sock.close()
            self.sock = None

    def setup_complete(self, *args, **kwargs):
        pass
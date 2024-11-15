from modules.executors.common import GenericExecutor

from websockets.sync.client import connect as ws_connect
from websockets.sync.server import serve as ws_serve

class WebsocketClientNode(GenericExecutor):
    node_type = "websocket_client"
    def __init__(self,node_graph_parameters):
        self.connection = None

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.address = conf["address"]
        self.enable_receive = conf.get("enable_receive",False)

    def __call__(self,prompt_args):
        if not self.connection:
            self.connection = ws_connect(self.address,close_timeout=1)
        if len(prompt_args) > 0:
            self.connection.send(prompt_args[0])
        if self.enable_receive:
            res = [self.connection.recv()]
        else:
            res = prompt_args

        return res
        
    def graph_started(self):
        pass
    
    def graph_stopped(self):
        if self.connection:
            self.connection.close()
            self.connection = None
        
    def setup_complete(self, *args, **kwargs):
        pass
        
        
class WebsocketServerNode(GenericExecutor):
    node_type = "websocket_server"
    def __init__(self,node_graph_parameters):
        self.data_to_client = []
        self.data_from_client = []

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.port = conf["port"]
        self.enable_receive = conf.get("enable_receive",False)

    def __call__(self,prompt_args):
        self.data_to_client = prompt_args
        #print(self.data_to_client)
        sock, addr = self.server.socket.accept()
        self.server.handler(sock,addr)

        return self.data_from_client
        
    def echo(self, websocket):
        for el in self.data_to_client:
            websocket.send(el)
        if self.enable_receive:
            res = websocket.recv()
            self.data_from_client = [res]
        
    def graph_started(self):
        self.server = ws_serve(self.echo, "0.0.0.0", self.port)
    
    def graph_stopped(self):
        self.server.socket.close()
        
    def setup_complete(self, *args, **kwargs):
        pass

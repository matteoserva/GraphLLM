from modules.executors.common import GenericExecutor

from websockets.sync.client import connect as wsconnect

class WebsocketClientNode(GenericExecutor):
    node_type = "websocket_client"
    def __init__(self,node_graph_parameters):
        pass

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.address = conf["address"]
        print("parameters", conf,kwargs)

    def __call__(self,prompt_args):
        res = prompt_args
        return res
        
    def graph_started(self):
        print("ws start")
    
    def graph_stopped(self):
        print("ws stop")
        
    def setup_complete(self, *args, **kwargs):
        self.connection = wsconnect(self.address)
        self.connection.send("Hello world!")
        message = self.connection.recv()
        self.connection.close()
        print(message)
        
        


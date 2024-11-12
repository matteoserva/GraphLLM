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
        self.enable_receive = conf.get("enable_receive",False)

    def __call__(self,prompt_args):
        self.connection.send(prompt_args[0])
        if self.enable_receive:
            res = [self.connection.recv()]
        else:
            res = prompt_args

        return res
        
    def graph_started(self):
        self.connection = wsconnect(self.address,close_timeout=1)
    
    def graph_stopped(self):
        self.connection.close()
        
    def setup_complete(self, *args, **kwargs):
        pass
        
        


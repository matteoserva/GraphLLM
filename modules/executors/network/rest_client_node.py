from modules.executors.common import GenericExecutor
import requests

class RestClientNode(GenericExecutor):
    node_type = "rest_client"
    def __init__(self, node_graph_parameters):
        self.session = None

    def initialize(self):
        pass

    def set_parameters(self, conf, **kwargs):
        self.url = conf["url"]
        self.method = conf.get("method", "GET")

    def __call__(self, prompt_args):
        if not self.session:
            self.session = requests.Session()
        
        if self.method == "GET":
            response = self.session.get(self.url)
        elif self.method == "POST":
            response = self.session.post(self.url, data=prompt_args[0] if prompt_args else "")
        elif self.method == "PUT":
            response = self.session.put(self.url, data=prompt_args[0] if prompt_args else "")
        elif self.method == "DELETE":
            response = self.session.delete(self.url)
        elif self.method == "PATCH":
            response = self.session.patch(self.url, data=prompt_args[0] if prompt_args else "")
        else:
            raise ValueError(f"Unsupported HTTP method: {self.method}")
        
        res = response.text

        return res
        
    def graph_started(self):
        pass
    
    def graph_stopped(self):
        if self.session:
            self.session.close()
            self.session = None
        
    def setup_complete(self, *args, **kwargs):
        pass

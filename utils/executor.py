from .formatter import PromptBuilder

def send_chat(builder,client):
    r = client.send_prompt(builder)
    ret = ""
    for line in r:
        print(line, end="", flush=True)
        ret = ret + line
    print("")
    return ret

class StatelessExecutor:
    def __init__(self,client):
        builder = PromptBuilder()
        builder.load_model(client.get_model_name())
        self.builder=builder
        self.client = client


    def __call__(self,m):
        builder = self.builder
        client = self.client

        builder.reset()
        messages = builder.add_request(m)
        prompt = builder._build()
        print(builder._build(),end="")
        res = send_chat(builder,client)
        messages = builder.add_response(str(res))
        return res

class StatefulExecutor:
    def __init__(self,client):
        builder = PromptBuilder()
        builder.load_model(client.get_model_name())
        self.builder=builder
        self.client = client

        self.print_prompt = True

    def __call__(self,m):
        builder = self.builder
        client = self.client

        messages = builder.add_request(m)
        prompt = builder._build()
        if self.print_prompt:
            print(builder._build(),end="")
        res = send_chat(builder,client)
        messages = builder.add_response(str(res))
        return res
    
class SequenceExecutor:
    pass
    #TODO

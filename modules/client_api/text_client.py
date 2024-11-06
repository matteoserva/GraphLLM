
class TextClientAPI:

    def get_user_input(self, inprompt="> "):
        return input(inprompt)

    def node_print(self,node_name,*args,**kwargs):
        print(*args, **kwargs)
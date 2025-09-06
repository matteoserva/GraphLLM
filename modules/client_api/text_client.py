
class TextClientAPI:

    def get_user_input(self, inprompt="> "):
        return input(inprompt)

    def node_print(self,node_name,*args,**kwargs):
        print(*args, **kwargs)


    def _not_implemented(self,function_name, node_name, *args,**kwargs):
        print("NOT IMPLEMENTED:",args,kwargs)

    def __getattr__(self, name):
        def wrapper(*args, **kwargs):
            return self._not_implemented(name, *args, **kwargs)
        return wrapper
class GraphException(Exception):


    def __init__(self,i, *args,**kwargs):

        if isinstance(i, GraphException):
            i = i.saved_i
        super().__init__(i)
        self.saved_i = i
        self.__traceback__ = i.__traceback__



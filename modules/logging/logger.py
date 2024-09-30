try:
    from extras.web_log import WebLogger
except:
    pass

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class WrappedWebLogger(metaclass=Singleton):
    def __init__(self,initialize=True):
       self.webLogger = None
       try:
            if initialize:
                webLogger = WebLogger(detach=False)
                webLogger.start()
                self.webLogger = webLogger
       except:
            pass

    def dummy(self,*args,**kwargs):
       pass

    def __getattr__(self,item):
       if self.webLogger:
          return getattr(self.webLogger,item)
       else:
          return self.dummy

    def stop(self):
        #print("wwl clear\n")
        if self.webLogger:
            self.webLogger.stop()
            self.webLogger = None

    def __del__(self):
        self.stop()

class Logger():
    def __init__(self):
        self.prints = {}
        self.webLogger = WrappedWebLogger()

    def log(self,type,*args,**kwargs):
        #
        if type == "names":
            if self.webLogger:
              pass#self.webLogger.set_nodes(args[0])
        if type == "print":
            print(*args[1:],**kwargs)
            self.prints[args[0]] = args[1]
            self.webLogger.set_output(args[0],args[1])
        if type == "output":
            values = [str(el) for el in args[1] ]
            values = "\n\n" + ",".join(values)
            #print(*args[1:],**kwargs)

            if args[0] not in self.prints:
               self.webLogger.set_output(args[0],values)

    def stop(self):
          pass
    def __del__(self):
          #print("logger exit")
          self.stop()

def stop_logger():
    #print("closeLogger")
    WrappedWebLogger(initialize=False).stop()

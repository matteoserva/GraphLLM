try:
    from extras.web_log import WebLogger
except:
    pass

class Logger:
    def __init__(self):
        self.webLogger = None
        try:
            webLogger = WebLogger(detach=False)
            webLogger.start()
            self.webLogger = webLogger
        except:
            pass
    
    def log(self,type,*args,**kwargs):
        #
        if type == "names":
            if self.webLogger:
              pass#self.webLogger.set_nodes(args[0])
        if type == "print":
            print(*args[1:],**kwargs)
            if self.webLogger:
              self.webLogger.set_output(args[0],args[1])
        if type == "output":
            values = [str(el) for el in args[1] ]
            values = "\n\n".join(values)
            #print(*args[1:],**kwargs)
            if self.webLogger:
               self.webLogger.set_output(args[0],values)

    def stop(self):
          if self.webLogger:
              self.webLogger.stop()
              self.webLogger = None




class Logger:
    def __init__(self):
        self.webLogger = None
        try:
            from extras.web_log import WebLogger
            webLogger = WebLogger()
            webLogger.start()
            self.webLogger = webLogger
        except:
            pass
    
    def log(self,type,*args):
        #print(args)
        if not self.webLogger:
            return
        if type == "names":
            self.webLogger.set_nodes(args[0])
        if type == "output":
            self.webLogger.set_output(args[0],args[1])

    

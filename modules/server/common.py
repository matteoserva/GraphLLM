

from  urllib.error import HTTPError

class HandlerException(HTTPError):
    def __init__(self, code=404):
        super().__init__(code=code, url="", msg="", hdrs="", fp="")
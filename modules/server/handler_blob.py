
class BlobHandler():

    def __init__(self):
        self.cache_data = [None]*10
        self.cache_head = 0
        self.add_binary_data(b"ciao")

    def add_binary_data(self,data):
        self.cache_data[self.cache_head] = data
        self.cache_head = (self.cache_head + 1) % 10

    def do_GET(self, server):
        server.close_connection = True
        http_path = server.path.split("?", 1)[0]
        split_path = http_path.split("/", 2)
        index = int(split_path[2])
        server.send_response(200)
        server.send_header('Connection', 'close')
        # self.send_header('Content-type', 'text/html')
        server.end_headers()
        server.wfile.write(self.cache_data[index])
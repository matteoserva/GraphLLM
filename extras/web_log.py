import justpy as jp
import threading

class WebLogger:
    def __init__(self,detach = True):
        self.wp = jp.WebPage(delete_flag=False)
        self.table = jp.Table(a=self.wp,style="")
        self.div_buttons = jp.Div(text="", a=self.wp)
        self.div_boxes = jp.Div(text="", a=self.wp)
        self.nodes = {}
        self.detach = detach
        self.loop = None
        #self.d = jp.Div(text='Not clicked yet', a=self.wp, classes='w-48 text-xl m-2 p-1 bg-blue-500 text-white')
        #self.d.on('click', self.my_click1)

    def _select_node(self,msg):
        #jp.jp_server.stop()
        obj = msg["target"]
        name = obj.p["name"]
        print(name)
        #for el_name in self.nodes:
        #    el = self.nodes[el_name]
        #    if el["name"] != name:
        #        el["box"].show = False
        obj.p["box"].show = not obj.p["box"].show
        #await obj.p["box"].update()

    def _create_node(self,node_name):
        el = node_name
        tr = jp.Tr(a=self.table)
        d = jp.Td(text=el, a=tr)
        d.on('click', self._select_node)
        d2 = jp.Td(text="", a=tr, style="border:1px solid black;")
        tb = jp.Pre(text="", a=d2, delete_flag=False,style="white-space: pre-wrap;")
        tb.add_page(self.wp)
        # tb.on('click', self._select_node)
        tb.show = True
        n = {"name": el, "button": d, "box": tb}
        d.p = n
        tb.p = n
        self.nodes[el] = n

    def set_nodes(self,node_names):
        for el in node_names:
            self._create_node(el)
        self._update()

    def set_output(self, name, value):
        if name not in self.nodes:
            self._create_node(name)
        node = self.nodes[name]
        box = node["box"]
        box.text = box.text + value
        #p =jp.Pre(text="")
        #box.add_component(p,0)
        self._update(box)


    def my_click1(self, msg):
        self.text = 'I was clicked'
        print("click")
        page.append(self)

    def event_demo1(self):
        return self.wp

    def _thread_main(self):
        jp.justpy(self.event_demo1,start_server=False)
        s = jp.get_server()
        s.config.setup_event_loop()
        try:
            with asyncio.Runner() as runner:
                self.loop = runner.get_loop()
                runner.run(s.serve())
        except:
            pass
        self.loop = None
    def start(self):
        t1 = threading.Thread(target=self._thread_main,args=())
        t1.daemon = self.detach

        t1.start()
        self.t1 = t1

    def stop(self):
        time.sleep(.5)
        s = jp.get_server()
        s.should_exit = True
        #s.force_exit = True

        self.t1.join()

    def _update(self, obj=None):
        if  obj is None:
            obj = self.wp
        if self.loop :
            #try:
            res = asyncio.run_coroutine_threadsafe(obj.update(),self.loop)
            _ = res.result()
            #except:
            #    self.loop = None
        
    def update(self,val):
        #self.d.text = str(val)
        self._update()
import asyncio
import time



if __name__ == "__main__":
    l = WebLogger(detach=False)
    l.start()
    l.set_nodes(["ciao1","ciao2"])
    a = 1
    time.sleep(2)

    #asyncio.run(s.shutdown())
    while True:
         a = a + 1
         l.set_output("ciao1",str(a))
         time.sleep(1)
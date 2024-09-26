import justpy as jp
import threading

class WebLogger:
    def __init__(self,detach = True):
        self.wp = jp.WebPage(delete_flag=False)
        self.div_buttons = jp.Div(text="", a=self.wp)
        self.div_boxes = jp.Div(text="", a=self.wp)
        self.nodes = {}
        self.detach = detach
        #self.d = jp.Div(text='Not clicked yet', a=self.wp, classes='w-48 text-xl m-2 p-1 bg-blue-500 text-white')
        #self.d.on('click', self.my_click1)

    def _select_node(self,msg):
        obj = msg["target"]
        name = obj.p["name"]
        print(name)
        for el_name in self.nodes:
            el = self.nodes[el_name]
            if el["name"] != name:
                el["box"].show = False
        obj.p["box"].show = True
        self._update()

    def set_nodes(self,node_names):
        for el in node_names:
            d = jp.Div(text=el, a=self.div_buttons)
            d.on('click', self._select_node)
            tb = jp.Div(text=el, a=self.div_boxes)
            #tb.on('click', self._select_node)
            tb.show = True
            n = {"name": el, "button": d, "box": tb}
            d.p = n
            tb.p = n
            self.nodes[el] = n

    def set_output(self, name, value):
        node = self.nodes[name]
        box = node["box"]
        box.text = value
        self._update()


    def my_click1(self, msg):
        self.text = 'I was clicked'
        print("click")
        page.append(self)

    def event_demo1(self):
        return self.wp
    
    def start(self):
        t1 = threading.Thread(target=jp.justpy,args=(self.event_demo1,))
        t1.daemon = self.detach
        t1.start()

    def _update(self):
        asyncio.run(self.wp.update())
        
    def update(self,val):
        #self.d.text = str(val)
        self._update()
import asyncio
import time



if __name__ == "__main__":
    l = WebLogger(detach=False)
    l.start()
    l.set_nodes(["ciao1","ciao2"])
    #a = 1
    #while True:
    #     a = a + 1
    #     l.update(a)
    #     time.sleep(1)
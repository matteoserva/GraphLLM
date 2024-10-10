
class WebBrige {
  constructor() {
    this.editor = editor;
    this.graph = editor.graph;
    this.canvas = this.editor.graphcanvas;
    this.saveBtn = document.querySelector("div.litegraph button#save")
  }

  connect() {
    let cb_as = this.graph.onAfterStep;
    let cb_bs = this.graph.onBeforeStep;
    let that = this
    this.graph.onAfterStep = function() {
        if(cb_as)
        	cb_as();
        let n=that.graph.getNodeById("1")
        that.canvas.selectNodes([n])
        that.editor.onPlayButton();
        that.graph.stop(); // per sicurezza
        console.log("afterStep chiamato");
    };
    this.saveBtn.addEventListener("click",this.save);

    this.graph.onBeforeStep = function()
    {
        if(cb_bs) {cb_bs();}
        console.log("before step")

    }

  }

  save() {
   var data = JSON.stringify( graph.serialize() );
   let xhr = new XMLHttpRequest();
   xhr.open('POST', '/graph/save',false);
   xhr.setRequestHeader("Content-Type", "application/json")
   xhr.send(data);
   console.log("save called")
  }
}

const web_bridge = new WebBrige();
web_bridge.connect()

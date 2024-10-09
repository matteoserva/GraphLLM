

class WebBrige {
  constructor() {
    this.editor = editor;
    this.graph = editor.graph;
  }
  
  connect() {
    let cb = this.graph.onAfterExecute;
    let that = this
    this.graph.onAfterExecute = function() {
        cb();
        that.editor.onPlayButton();
        that.graph.stop(); // per sicurezza
        console.log("afterExecute chiamato");
    };
  
  }
}

const web_bridge = new WebBrige();
web_bridge.connect()
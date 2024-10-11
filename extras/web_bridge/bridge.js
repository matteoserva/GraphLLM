
function addDemo( name, url )
{
	var option = document.createElement("option");
	if(url.constructor === String)
		option.dataset["url"] = url;
	else
		option.callback = url;
	option.innerHTML = name;
	select.appendChild( option );
}



class WebBrige {
  constructor() {
    this.editor = editor;
    this.graph = editor.graph;
    this.canvas = this.editor.graphcanvas;
    this.saveBtn = document.querySelector("div.litegraph button#save")
  }

  connect() {
    this.cb_as = this.graph.onAfterStep;
    let cb_bs = this.graph.onBeforeStep;
    let that = this
    this.graph.onAfterStep = this.onAfterStep.bind(this)
    this.saveBtn.addEventListener("click",this.save);

    this.graph.onBeforeStep = function()
    {
        if(cb_bs) {cb_bs();}
        //console.log("before step")

    }
    this.graph.onPlayEvent = this.onPlayEvent.bind(this)
    this.graph.onStopEvent = this.onStopEvent.bind(this)
    
    //some examples
    //addDemo("rap battle", "/graph/load?file=rap_battle.json");
    this.loadList()
  }

  loadList()
  {
    var data = JSON.stringify( graph.serialize() );
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/graph/list',false);
    
    var response = xhr.send(data);
    var lines = xhr.responseText.split("\n")
    lines.forEach((element) => {addDemo(element, "/graph/load?file="+element); });
    console.log(xhr.responseText)
  }
  
  onPlayEvent()
  {
      this.controller = new AbortController();
      const signal = this.controller.signal;
      console.log("play")
      let that = this
      var data = JSON.stringify( graph.serialize() );
      fetch('/graph/exec',{ signal:signal, method:"POST", body:data}).then(response => {
                  var text = '';
            var reader = response.body.getReader()
            var decoder = new TextDecoder();
            var t = that
            
            return readChunk();

            function readChunk() {
              return reader.read().then(appendChunks);
            }

            function appendChunks(result) {
              var chunk = decoder.decode(result.value || new Uint8Array, {stream: !result.done});
              //console.log('got chunk of', chunk.length, 'bytes')
              //text += chunk;
              
              t.processChunk(chunk);
              if (result.done) {
                
                //console.log('returning')
                return text;
              } else {
                
                //console.log('recursing')
                return readChunk();
              }
            }
      }
      ).then(onChunkedResponseComplete)  .catch(onChunkedResponseError);
            function onChunkedResponseComplete(result) {
          console.log('all done!', result)
          window.setTimeout(that.stopGraph,200)
        }

        function onChunkedResponseError(err) {
          that.stopGraph()
          console.error(err)
        }
  }
  
  processChunk(chunk)
  {
      var lines = chunk.split("\n")
      lines.forEach((element) => {if (element.length > 0) {this.processMessage(element)}});
      
  }
  
  processMessage(text)
  {
      var obj = JSON.parse(text);
      if(obj.type == "output")
      {
        var name = obj.data[0].substr(1)
        var values = obj.data[1]
        var n = this.graph.getNodeById(name)
        if(n && values.length > 0)
        {
          for(let i = 0; i < values.length; i++)
            
            n.setOutputData(i,values[i])
        }
      }
      if(obj.type == "running")
      {
        var values = obj.data[0]
        var names = values.map((el) => el.substr(1));
        var nodes = names.map((el) => this.graph.getNodeById(el));
        this.canvas.selectNodes(nodes)
      }
      if(obj.type != "print")
      {
        console.log(text, '\n');
      }
  }
  
  onStopEvent()
  {
      this.controller.abort("stopGraph");
      console.log("stop")
  }
  
  onAfterStep()
  {
     if(this.cb_as)
        	this.cb_as();
        let n=this.graph.getNodeById("1")
        //this.canvas.selectNodes([n])
        //
        //
        //console.log("afterStep chiamato");
  }
  
  stopGraph()
  {
    if (graph.status != LGraph.STATUS_STOPPED) {
      this.editor.onPlayButton();
    }
    this.graph.stop(); // per sicurezza
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


function addDemo( select, name, url )
{
	var option = document.createElement("option");
	/*if(url.constructor === String)
		option.dataset["url"] = url;
	else
		option.callback = url;*/
	option.innerHTML = name;
	select.appendChild( option );
}



class WebBrige {
  constructor() {
    this.editor = editor;
    this.graph = editor.graph;
    this.canvas = this.editor.graphcanvas;
    this.topBar = document.querySelector("span#LGEditorTopBarSelector")
    this.topBar.innerHTML ="Graphs: <span><input id='filename' maxlength='50' style='height: 30px; min-width:400px'/><select style='height: 30px; width:20px'><option>Empty</option></select></span><button class='btn' id='save'>Save</button><button class='btn' id='load'>Load</button><button class='btn' id='delete'>Delete</button><button class='btn' id='new'>New</button><button class='btn' id='download'>Download</button> | ";

    this.saveBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#save")
    this.loadBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#load")
    this.deleteBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#delete")
    this.newBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#new")
    this.nameSelector = document.querySelector("div.litegraph .selector input#filename")
    this.select = document.querySelector("div.litegraph .selector select")

  }

  connect() {
    this.cb_as = this.graph.onAfterStep;
    let cb_bs = this.graph.onBeforeStep;
    let that = this



    this.graph.onAfterStep = this.onAfterStep.bind(this)
    this.saveBtn.addEventListener("click",this.save.bind(this));
    this.loadBtn.addEventListener("click",this.load.bind(this));
    this.deleteBtn.addEventListener("click",this.deleteFile.bind(this));
    this.newBtn.addEventListener("click",this.newGraph.bind(this));
    document.querySelector("div.tools #playstepnode_button").remove()
    document.querySelector("div.tools #livemode_button").remove()
    document.querySelector("div.litegraph > div.header").style.zIndex = 1
    document.querySelector("div.litegraph div.headerpanel.loadmeter").style.display="none"
    document.querySelector("div.litegraph div.content").style.overflow="hidden"
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
    this.select.addEventListener("change", function(e){
            if(this.select.selectedIndex > 0)
            {
                this.select.previousElementSibling.value=this.select.value;
                this.select.previousElementSibling.focus()
                this.select.selectedIndex = 0
                this.load()
            }

        }.bind(this));
    document.addEventListener('keydown', (event) => {
        if(event.ctrlKey && event.key == "Enter") {
            this.startGraph()
        }
    });
  }

  loadList()
  {
    var data = JSON.stringify( graph.serialize() );
    let xhr = new XMLHttpRequest();
    xhr.open('GET', '/graph/list',false);

    this.select.innerHTML = "<option>--select--</option>"
    var response = xhr.send(data);
    var lines = xhr.responseText.split("\n")
    lines.forEach((element) => {addDemo(this.select, element, "/graph/load?file="+element); });
    console.log(xhr.responseText)
    this.select.selectedIndex = 0
  }
  
  onPlayEvent()
  {
      this.controller = new AbortController();
      const signal = this.controller.signal;
      console.log("play")
      let that = this
      var data = JSON.stringify( graph.serialize() );
      this.socket = new WebSocket("ws://" + window.location.host + "/graph/exec");
      var socket = this.socket
      socket.addEventListener("open", (event) => {
          socket.send(data);
        });
      socket.addEventListener("message", (event) => {
          this.processMessage(event.data)
        });
      socket.addEventListener("close", (event) => {
          window.setTimeout(this.stopGraph,200)
        });
      socket.addEventListener("error", (event) => {
          this.stopGraph()
		  console.error(event.data)
        });

      /*fetch('/graph/exec',{ signal:signal, method:"POST", body:data}).then(response =>
            {
                    var text = '';
                    var buffer = {text: ""}
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

                          t.processChunk(buffer, chunk);
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
		  if (err.name != "stopGraph" && err.name != "AbortError")
		  {
          var message = "error: " + err
          alert(message)
		  }
        }*/
  }

  /*
  processChunk(buffer, chunk)
  {
      buffer.text += chunk
      var lines = buffer.text.split("\n")
      buffer.text = lines.pop()
      lines.forEach((element) => {if (element.length > 0) {this.processMessage(element)}});

  }*/

  processMessage(text)
  {
      var obj = JSON.parse(text);

      if(obj.type == "output")
      {
        var name = obj.data[0].substr(1)
        var values = obj.data[1]
        var n = this.graph.getNodeById(name)
        if(!!n)
        {
          if(values.length > 0)
          {
            for(let i = 0; i < values.length; i++)

              n.setOutputData(i,values[i])
          }
        }
      }
      if(obj.type == "error")
      {
        var message = "error: " + obj.data[0]
        console.log(message)
        alert(message)
      }
      /*if(obj.type == "running")
      {
        var values = obj.data[0]
        var names = values.map((el) => el.substr(1));
        var nodes = names.map((el) => this.graph.getNodeById(el));
        nodes = nodes.filter(function( element ) { return !!element;    });
        this.canvas.selectNodes(nodes)
        for (let index = 0; index < nodes.length; ++index) {
			let node = nodes[index]
					if(node.outputs && node.outputs.length > 0) { node.print_log = ""}
		}
      }*/
	  if(obj.type == "starting")
      {
		  var name = obj.data[0].substr(1)
		  var node = this.graph.getNodeById(name)
		  if (node)
		  {
			 this.canvas.selectNode(node,true);
			 if(node.outputs && node.outputs.length > 0) { node.print_log = ""}
		  }
          
      }
	  if(obj.type == "stopping")
      {
        var name = obj.data[0].substr(1)
		  var node = this.graph.getNodeById(name)
		  if (node)
		  {
			 this.canvas.deselectNode(node);
		  }
      }
      if(obj.type == "print")
      {
         var name = obj.data[0].split("/")[1]
         var value = obj.data[1]
         var n = this.graph.getNodeById(name)
         if((!!n) && n.outputs && n.outputs.length > 0)
         {
             var old = n.print_log || ""
             var newVal = old + value
             n.print_log = newVal
             n.setOutputData(0,newVal)
	 }
      }

      if(obj.type != "print")
      {
        console.log(text, '\n');
      }
  }
  
  onStopEvent()
  {
      this.socket.close()
      this.controller.abort({name:"stopGraph"});
      console.log("stop")
      this.canvas.selectNodes([])
  }
  
  onAfterStep()
  {
     if(this.cb_as)
        	this.cb_as();
  }

  startGraph()
  {
    var isStopped = (graph.status == LGraph.STATUS_STOPPED)
    if(isStopped)
    {
        this.editor.onPlayButton();
    }
  }

  stopGraph()
  {
    var wasRunning = (graph.status != LGraph.STATUS_STOPPED);
    if (wasRunning) {
      this.editor.onPlayButton();
    }
    this.graph.stop(); // per sicurezza
    if(wasRunning)
    {
	this.graph.runStep();
    }
  }
  
  save() {
    var e = this.nameSelector
    var value = e.value;
   var data = JSON.stringify( graph.serialize() );
   let xhr = new XMLHttpRequest();
   xhr.open('POST', '/graph/save?file=' + value,false);
   xhr.setRequestHeader("Content-Type", "application/json")
   xhr.send(data);
   console.log("save called")
   this.loadList()
  }

  deleteFile() {
   //this.graph.clear()
    var e = this.nameSelector
    var value = e.value;
   var data = JSON.stringify( graph.serialize() );
   let xhr = new XMLHttpRequest();
   xhr.open('POST', '/graph/delete?file=' + value,false);
   xhr.setRequestHeader("Content-Type", "application/json")
   xhr.send(data);
   console.log("delete called")
   this.loadList()
   this.nameSelector.value = ""
  }

  newGraph() {
   this.graph.clear()
   this.nameSelector.value = ""
  }

  load() {
    var e = this.nameSelector
    var value = e.value;

   let xhr = new XMLHttpRequest();
   xhr.open('GET', '/graph/load?file=' + value,false);
   xhr.setRequestHeader("Content-Type", "application/json")
   xhr.send();
   var data = xhr.responseText
   if(data)
        var parsed = JSON.parse( data )
        if(parsed && parsed.nodes)
        {
            var registered_types = LiteGraph.registered_node_types
            var registered_basetypes = {}
            for (var key in registered_types)
            {
                var baseName = key.split("/").reverse()[0]
                registered_basetypes[baseName] = key
            }
            var nodes = parsed.nodes
            var missing_nodes = nodes.filter(function( element ) { return !(element.type in registered_types)});
            missing_nodes.map(function( element ) {element.type = registered_basetypes[element.type.split("/").reverse()[0]] })

        }
        graph.configure( parsed );
        window.setTimeout(graph.change.bind(graph))
   console.log("load called")
  }
}

const web_bridge = new WebBrige();
web_bridge.connect()

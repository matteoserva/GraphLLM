
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
    var topbar_html = "Graphs: <span style=\"display: inline-block;position:relative;width: 460px; height: 35px;\" >"
    topbar_html += "<input id='filename' maxlength='50' style='height: 100%; width:400px;position: relative;'/><select class=\"selector-main\" style='height: 100%; width:430px; position: absolute; top:0px; right: 30px'><option>Empty</option></select><select class=\"selector-extras\" style='height: 100%; width:460px; position: absolute; top:0px; right: 0px'><option>Empty</option></select></span>"
    topbar_html += "<span class=\"tool_buttons\"><button class='btn' id='save'>Save</button><button class='btn' id='load'>Load</button><button class='btn' id='delete'>Delete</button><button class='btn' id='new'>New</button><button class='btn' id='download'>Download</button></span>| ";
    this.topBar.innerHTML = topbar_html

    this.saveBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#save")
    this.loadBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#load")
    this.deleteBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#delete")
    this.newBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#new")
    this.nameSelector = document.querySelector("div.litegraph .selector input#filename")
    this.select = document.querySelector("div.litegraph .selector .selector-main")

    this.audio = new Audio();
  }

  setDefaultConnectionEndpoints()
  {
    LiteGraph.slot_types_default_out.string=["output/watch"]
    LiteGraph.slot_types_default_in.string=["input/text_input"]
  }

  processMouseDown(e)
  {
    if (this.canvas.selected_group)
    {
        if (this.canvas.selected_group.collapse_state && this.canvas.selected_group.collapse_state.is_collapsed &&this.canvas.selected_group_resizing)
        {
            this.canvas.selected_group_resizing = false
            this.canvas.selected_group.recomputeInsideNodes();
        }
    }
    if (this.canvas.node_dragged)
    {
        var draggable = true;
        for (let el in this.graph._groups)
        {
            var group = this.graph._groups[el]
            if(group.collapse_state && group.collapse_state.is_collapsed)
            {
                if(!this.canvas.node_dragged)
                {
                    console.log("strano")
                }

                var managed_nodes = Object.keys(group.collapse_state.node_info)
                if( managed_nodes.includes('' + this.canvas.node_dragged.id) )
                {
                    draggable = false
                }
            }
        }
        if(!draggable)
        {
            this.canvas.node_dragged = null
            }

    }


  }
  processMouseUp(e)
  {

          var now = LiteGraph.getTime();
        var previousClick = this.previousClick || [0,0]
        this.previousClick = [now,this.canvas.last_mouseclick].concat( [previousClick[0], previousClick[1]])
        var total = this.previousClick[0] - this.previousClick[3]
        var t1 = (this.previousClick[0] - this.previousClick[1])
        var t2 = (this.previousClick[2] - this.previousClick[3])
        var is_double_click = (total < 300) && (t1 > 1) && (t2 > 1) && (t1 < 100) && (t2 < 100)

		var is_primary = (e.isPrimary === undefined || e.isPrimary);
        is_double_click = is_double_click && is_primary;
        var should_handle = this.canvas.selected_group && is_double_click
        if(should_handle)
        {
            var group = this.canvas.selected_group
            if (group.collapse_state === undefined)
            {
                group.collapse_state = { is_collapsed: false, node_info: new Object()}
            }
            if (group.collapse_state.is_collapsed)
            {
                group.collapse_state.is_collapsed = false
                for (var i = 0; i < group._nodes.length; ++i) {
                    var node = group._nodes[i];
                    var id = '' + node.id

                    if(Object.keys(group.collapse_state.node_info).includes(id))
                    {
                        var node_info = group.collapse_state.node_info[id]
                        node.pos = [group.pos[0]+node_info.pos[0], group.pos[1] + node_info.pos[1]]
                        if (node.flags.collapsed && !node_info.collapsed)
                        {
                            node.collapse()
                        }

                    }
                }
                group.size = group.collapse_state.group_size
                group.color = group.collapse_state.color
                //
            }
            else
            {
                for (var i = 0; i < group._nodes.length; ++i) {
                    var node = group._nodes[i];
                    var delta_pos = [ node.pos[0] - group.pos[0],  node.pos[1] - group.pos[1]]
                    var new_pos = [ group.pos[0] + 20,   group.pos[1] + 70]
                    group.collapse_state.node_info[node.id] = {id: node.id, size: node.size, pos: delta_pos, collapsed: node.flags.collapsed}

                    if(!node.flags.collapsed)
                    {
                        node.collapse()
                    }
                    node.pos = new_pos


                }
                var internal_nodes = group._nodes.map((n) => ''+n.id)
                // remove nodes not in group
                var node_info = group.collapse_state.node_info
                node_info = Object.keys(node_info).filter((k) => internal_nodes.includes(k)).reduce((cur,key) => { return Object.assign(cur, { [key]: node_info[key] })}, {});
                group.collapse_state.node_info = node_info
                group.collapse_state.group_size = [...group.size]
                group.size = [180,110]
                group.collapse_state.color = group.color
                group.color = "#606060"
                group.collapse_state.is_collapsed = true

            }
        }
        //console.log("group: " + this.canvas.selected_group + "   double " + is_double_click + "   time: "
        //+ (now - this.canvas.last_mouseclick), " p " + this.previousClick + "  t " + [total,t1,t2])

    return false;
  }

  connect() {
    this.setDefaultConnectionEndpoints()

    this.canvas.allow_searchbox = false

    this.canvas.onMouseDown = this.processMouseDown.bind(this)
    LiteGraph.pointerListenerAdd(document,"up", this.processMouseUp.bind(this),true);
    this.cb_as = this.graph.onAfterStep;
    let cb_bs = this.graph.onBeforeStep;
    let that = this

    this.topBar.appendChild(this.audio)

    this.graph.onAfterStep = this.onAfterStep.bind(this)
    this.saveBtn.addEventListener("click",this.save.bind(this));
    this.loadBtn.addEventListener("click",this.load.bind(this));
    this.deleteBtn.addEventListener("click",this.deleteFile.bind(this));
    this.newBtn.addEventListener("click",this.newGraph.bind(this));
    document.querySelector("div.tools #playstepnode_button").remove()
    document.querySelector("div.tools #livemode_button").remove()
    document.querySelector("div.litegraph div.headerpanel.loadmeter").style.display="none"
    document.querySelector("div.litegraph div.content").style.overflow="hidden"
    this.graph.onBeforeStep = function()
    {
        if(cb_bs) {cb_bs();}
        //console.log("before step")

    }
    this.graph.onPlayEvent = this.onPlayEvent.bind(this)
    this.graph.onStopEvent = this.onStopEvent.bind(this)
    this.graph.onSerialize = this.onSerialize.bind(this)
    this.graph.onConfigure= this.onDeserialize.bind(this)

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

  startWebSocket(data)
  {
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
          if(!event.wasClean)
          {
            alert("connection lost")
          }
        });
      socket.addEventListener("error", (event) => {
          this.stopGraph()
		  console.error(event.data)
        });
  }

  stopWebSocket()
  {
    this.socket.close()
  }

  onPlayEvent()
  {

      console.log("play")
      this.listeners = {}
      var listeners = this.listeners
      this.graph.sendEventToAllNodes("connectPublishers",subscribe)
      var data = JSON.stringify( graph.serialize() );
      this.startWebSocket(data)

      function subscribe(current_node, source_location, eventId, action)
      {
         if(!(listeners[eventId.type]))
         {
            listeners[eventId.type] = []
         }
         if(source_location.position.toLowerCase() == "input")
         {
             var source_node = current_node.getInputNode(source_location.slot);
         }
         else if (source_location.position.toLowerCase() == "output")
         {
             var source_nodes = current_node.getOutputNodes(source_location.slot)
             var filter = "llm_call"
             source_nodes = source_nodes.filter((element)=>element.type.endsWith(filter));
             if (source_nodes.length == 1)
             {
                var source_node = source_nodes[0]
             }
         }

         var shouldAbort = false
         if(source_node)
         {
            eventId.source = source_node.id.toString()
         }
         else
         {
            shouldAbort = true
         }

         if ((!shouldAbort) && source_location.position.toLowerCase() == "input" && !("slot" in eventId))
         {
             var inputLink = current_node.getInputLink(source_location.slot)

             // check direct connections
             if(eventId.type == "output")
             {
                eventId.slot = inputLink.origin_slot
             }
             if(eventId.type == "print" && inputLink.origin_slot > 0)
             {
                shouldAbort = true
             }

         }

         if(!shouldAbort)
         {
            var typelistener = listeners[eventId.type]
            typelistener.push([eventId, action_set])
         }
         //console.log(eventId ,callback)
         function action_set(eventId,eventData)
         {
              current_node.container.executeAction(eventId, action, eventData)
         }
      }




  }

  notifyListeners(eventId, eventData )
  {
        var typeListeners = this.listeners[eventId.type] || []
        typeListeners = typeListeners.filter(eventFilter)
        typeListeners.map(executeCallback)
        //console.log(eventId, eventData);

        function eventFilter(element)
        {
            var f1 = eventId.source == element[0].source;
            var f2 = eventId.type == element[0].type;
            var f3 = (!("slot" in element[0])) || (eventId.slot == element[0].slot);
            var res = f1 && f2 && f3;
            return res;
        }

        function executeCallback(element)
        {
            var callback = element[1]
            callback(eventId,eventData)
        }
  }

  processChunk(buffer, chunk)
  {
      buffer.text += chunk
      var lines = buffer.text.split("\n")
      buffer.text = lines.pop()
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
            if((!!n) && values.length > 0)
            {

                for(let i = 0; i < values.length; i++)
                {
                      var string = new String(values[i]);
                      string.graphllm_type="output"
                      string.text_content=values[i]
                      n.setOutputData(i,string)

                      var eventId = {type: obj.type, source: name, slot: i}
                      var value = values[i]
                      if (value != null)
                      {
                        this.notifyListeners(eventId, values[i])
                      }
                }

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
             var string = new String(newVal);
             string.graphllm_type="print"
             string.text_content=newVal
             n.setOutputData(0,string)

             var eventId = {type: obj.type, source: name}
             this.notifyListeners(eventId, value)
	     }
      }

      if(obj.type == "error")
      {
        var message = "error: " + obj.data[0]
        console.log(message)
        alert(message)
      }
      if(obj.type == "request")
      {
            if(obj.subtype == "audio")
              {
                var ref = obj.address
                ref = "/blob/" + ref
                console.log(ref)
                this.audio.src = ref
                this.audio.load();
                var req_id = obj.id
                var socket = this.socket
                this.audio.onended = function() {
                    console.log("play ended");
                    socket.send( JSON.stringify({type: "response", subtype: "audio", id: req_id}))
                };
                this.audio.onerror = function() {
                    console.log("play error");
                    //avoid duplicate response: socket.send( JSON.stringify({type: "response", subtype: "audio", id: req_id}))
                };
                this.audio.play().then(_ => {console.log("play started")}).catch((error) => {
                      socket.send( JSON.stringify({type: "response", subtype: "audio", id: req_id}))
                      console.error(error);
                    });;

              }



      }


      if(obj.type == "running")
      {
        /*var values = obj.data[0]
        var names = values.map((el) => el.substr(1));
        var nodes = names.map((el) => this.graph.getNodeById(el));
        nodes = nodes.filter(function( element ) { return !!element;    });
        this.canvas.selectNodes(nodes)
        for (let index = 0; index < nodes.length; ++index) {
			let node = nodes[index]
					if(node.outputs && node.outputs.length > 0) { node.print_log = ""}
		}*/
      }
	  if(obj.type == "starting")
      {
		  var name = obj.data[0].substr(1)
		  var node = this.graph.getNodeById(name)
		  if (node)
		  {
			 this.canvas.selectNode(node,true);
			 if(node.outputs && node.outputs.length > 0) { node.print_log = ""}
			 var eventId = {type: obj.type, source: name}
             this.notifyListeners(eventId)
		  }
          
      }
      if(obj.type == "call")
      {
		  var name = obj.data[0].substr(1)
		  var node = this.graph.getNodeById(name)
		  if (node)
		  {
			 var func = obj.data[1]
			 var val = obj.data[2]
			 node[func](val)
		  }

      }
	  if(obj.type == "stopping")
      {
          var name = obj.data[0].substr(1)
		  var node = this.graph.getNodeById(name)
		  if (node)
		  {
			 this.canvas.deselectNode(node);
			 var eventId = {type: obj.type, source: name}
             this.notifyListeners(eventId)
		  }
      }


      if(obj.type != "print")
      {
        console.log(text, '\n');
      }
  }
  
  onStopEvent()
  {
      this.stopWebSocket()

      this.audio.pause()
      console.log("stop")
      this.canvas.selectNodes([])
  }
  
  onAfterStep()
  {
     if(this.cb_as)
        	this.cb_as();
  }

  onSerialize(data)
  {
    var group_states = new Object()
    for(let el in data.groups)
    {
        var group = this.graph._groups[el]
        if ("collapse_state" in group)
        {
            group_states[el] = group.collapse_state
        }
    }
    data["group_states"] = group_states
    var e = this.nameSelector
    var value = e.value;
    data["graph_name"] = value

  }

  onDeserialize(data)
  {
    if ("group_states" in data)
    {
        for(let el in data.group_states)
        {
            var group = this.graph._groups[el]
            group.collapse_state = data.group_states[el]
        }

    }
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
   xhr.addEventListener("error", (event) => {alert("server error")});
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

  loadBackup()
  {
    var data = localStorage.getItem("litegraphg demo backup");
	if(!data)
		return;
	var graph_data = JSON.parse(data);
	this.graph.configure( graph_data );
    if ("graph_name" in graph_data)
    {
        var e = this.nameSelector;
        e. value = graph_data["graph_name"]
    }
  }
}

const web_bridge = new WebBrige();
web_bridge.connect()
web_bridge.loadBackup()
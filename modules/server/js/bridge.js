function addDemo(select, name, url) {
    var option = document.createElement("option");
    /*if(url.constructor === String)
    	option.dataset["url"] = url;
    else
    	option.callback = url;*/
    option.innerHTML = name;
    select.appendChild(option);
}

class BridgeNode {
	constructor() {
		self.server_lost = false
	}
	
	node_call(node, function_name, args) {
        const keys = function_name.match(/[^.\[\]]+/g);
        let func = keys.reduce(
            (current, key) => {
                return key
            },
            node
        )
        let parent = keys.slice(0, -1).reduce(
            (current, key) => {
                return current[key]
            },
            node
        )

        let result = parent[func].apply(parent, args)
        return result
    }

    node_assign(node, function_name, value) {
        const keys = function_name.match(/[^.\[\]]+/g);
        let func = keys.reduce(
            (current, key) => {
                return key
            },
            node
        )
        let parent = keys.slice(0, -1).reduce(
            (current, key) => {
                return current[key]
            },
            node
        )

        parent[func] = value
    }
	
	enqueueGuiEvent(node, action_name, args, responseCB)
	{
		let rpc_arguments = {
			//node: node.serialize(),
			node: node["type"],
			node_id: node["id"],
			event: action_name,
			arguments: args
		}
		var data = JSON.stringify(rpc_arguments);
		let xhr = new XMLHttpRequest();
		xhr.onloadend = (event) => {
			if(xhr.status != 0)
			{
				var response = JSON.parse(xhr.responseText)
				response.forEach((el) => responseCB(el))

				self.server_lost = false
				//console.log("GUI action response:", response)
			}
			else
			{
			    if(!self.server_lost)
			    {
				    alert("error sending event to server")
				}
				self.server_lost = true
			}
		};
		
		xhr.open('POST', '/editor/gui_action');
		xhr.setRequestHeader("Content-Type", "application/json")
		xhr.send(data);
	}
}


class WebBrige {
    constructor() {
		this.bridge_node = new BridgeNode()
        this.editor = editor;
        this.graph = editor.graph;
        this.canvas = this.editor.graphcanvas;
        this.topBar = document.querySelector("span#LGEditorTopBarSelector")
        var topbar_html = "Graphs: <span class=\"selector-bar\" style=\"display: inline-block;position:relative;width: 550px; height: 35px;\" >"
        topbar_html += "<select id=\"selector-folder\" style='height: 100%; width:150px; position: absolute; top:0px; left: 0px'><option>.</option></select>"
        topbar_html += "<input id='filename' maxlength='50' style='height: 100%; width:370px; right: 30px; position: absolute;'/><select class=\"selector-main\" style='height: 100%; width:400px; position: absolute; top:0px; right: 0px'><option>Empty</option></select></span>"
        //topbar_html += "<select class=\"selector-extras\" style='height: 100%; width:460px; position: absolute; top:0px; right: 0px'><option>Empty</option></select>"
        topbar_html += "<span class=\"tool_buttons\"><button class='btn' id='save'>Save</button><button class='btn' id='load'>Load</button><button class='btn' id='delete'>Delete</button><button class='btn' id='new'>New</button><button class='btn' id='download'>Download</button></span>| ";
        this.topBar.innerHTML = topbar_html

        this.saveBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#save")
        this.loadBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#load")
        this.deleteBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#delete")
        this.newBtn = document.querySelector("div.litegraph span#LGEditorTopBarSelector button#new")
        this.nameSelector = document.querySelector("div.litegraph .selector input#filename")
        this.select = document.querySelector("div.litegraph .selector .selector-main")
        this.select_folder = document.querySelector("div.litegraph .selector-bar #selector-folder")
        this.audio = new Audio();

        this.graph_handler = new GraphHandler(this, this.graph, this.canvas)
    }

    setDefaultConnectionEndpoints() {
        LiteGraph.slot_types_default_out.string = ["output/watch", "graph/virtual_sink"]
        LiteGraph.slot_types_default_in.string = ["input/text_input", "graph/virtual_source"]
        LiteGraph.slot_types_default_out.virtual = ["graph/virtual_source"]
        LiteGraph.slot_types_default_in.virtual = ["graph/virtual_sink"]
    }



    connect() {
        this.setDefaultConnectionEndpoints()
        this.graph_handler.connect()

        this.canvas.allow_searchbox = false
        this.canvas.align_to_grid = true
        this.graph.config.align_to_grid = true
        this.graph.bridge = {}

        this.cb_as = this.graph.onAfterStep;
        let cb_bs = this.graph.onBeforeStep;
        let that = this

        this.topBar.appendChild(this.audio)

        this.graph.onAfterStep = this.onAfterStep.bind(this)
        this.saveBtn.addEventListener("click", this.save.bind(this));
        this.loadBtn.addEventListener("click", this.load.bind(this));
        this.deleteBtn.addEventListener("click", this.deleteFile.bind(this));
        this.newBtn.addEventListener("click", this.newGraph.bind(this));
        document.querySelector("div.tools #playstepnode_button").remove()
        document.querySelector("div.tools #livemode_button").remove()
        document.querySelector("div.litegraph div.headerpanel.loadmeter").style.display = "none"
        document.querySelector("div.litegraph div.content").style.overflow = "hidden"
        this.graph.onBeforeStep = function() {
            if (cb_bs) {
                cb_bs();
            }
            //console.log("before step")

        }
        this.graph.onPlayEvent = this.onPlayEvent.bind(this)
        this.graph.onStopEvent = this.onStopEvent.bind(this)
        this.graph.onSerialize = this.onSerialize.bind(this)
        this.graph.onConfigure = this.onDeserialize.bind(this)

        //some examples
        //addDemo("rap battle", "/graph/load?file=rap_battle.json");

        this.select.addEventListener("change", function(e) {
            if (this.select.selectedIndex > 0) {
                this.select.previousElementSibling.value = this.select.value;
                this.select.previousElementSibling.focus()
                this.select.selectedIndex = 0
                this.load()
            }

        }.bind(this));
        this.select_folder.addEventListener("change", function(e) {
            this.loadList()
            this.nameSelector.value = ""
        }.bind(this));

        document.addEventListener('keydown', (event) => {
            var input_handled = true;
            if (event.ctrlKey && event.key == "Enter") {
                this.startGraph()
            } else if (event.ctrlKey && event.key == "r") {
                var selectedNodes = this.canvas.selected_nodes
                for (var i in selectedNodes) {
                    var node = this.canvas.selected_nodes[i];
                    var nodeRotation = node.node_rotation || 0
                    nodeRotation = (nodeRotation + 1) % 4;
                    this.setNodeRotation(node, nodeRotation)

                }
            } else if (event.ctrlKey && event.key == "s") {
                this.save()
            } else {
                input_handled = false
            }

            if (input_handled) {
                event.preventDefault()
                event.stopPropagation()
            }


        });



    }

    setNodeRotation(node, r) {
        var offset = LiteGraph.NODE_SLOT_HEIGHT * 0.5
        node.horizontal = (r % 2);
        node.flipped = r >= 2;

        node.node_rotation = r
    }

    loadList() {
		this.select.innerHTML = "<option>--Loading...--</option>"
        let xhr = new XMLHttpRequest();
		
		xhr.onerror = (e) => {
			this.select.innerHTML = "<option>--Error--</option>"
		}
		
		xhr.onload = (e) => {
			
			var lines = xhr.responseText.split("\n")
			this.select.innerHTML = "<option>--select--</option>"

			// extract folder names
			var folderNames = new Set();
			var fileData = []
			lines.forEach(filePath => {
				const parts = filePath.split('/');
				if (parts.length > 1) {
					folderNames.add(parts[0]);
					fileData.push({
						folder: parts[0],
						file: parts[1],
						path: filePath
					})
				} else {
					folderNames.add(".");
					fileData.push({
						folder: ".",
						file: parts[0],
						path: filePath
					})
				}
			});
			folderNames = Array.from(folderNames).sort();

			var selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text
			this.select_folder.innerHTML = ""
			folderNames.forEach((element) => {
				var option = document.createElement("option");
				option.innerHTML = element;
				this.select_folder.appendChild(option);
			});
			let folderIndex = folderNames.indexOf(selectedFolder);
			this.select_folder.selectedIndex = folderIndex >= 0 ? folderIndex : 0;
			selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text;

			fileData.forEach((element) => {
				if (element.folder == selectedFolder) addDemo(this.select, element.file, "/graph/load?file=" + element.path);
			});
			console.log("available graphs:", lines)
			this.select.selectedIndex = 0

			let bridge = this.graph.bridge
			bridge.graphs_list = lines
		}
		
        xhr.open('GET', '/graph/list');
        xhr.send({});
        
    }

    startWebSocket(data) {
        this.socket = new WebSocket("ws://" + window.location.host + "/graph/exec");
        var socket = this.socket
        socket.addEventListener("open", (event) => {
            socket.send(data);
        });
        socket.addEventListener("message", (event) => {
            this.processMessage(event.data)
        });
        socket.addEventListener("close", (event) => {
            window.setTimeout(this.stopGraph, 200)
            if (!event.wasClean) {
                alert("connection lost")
            }
        });
        socket.addEventListener("error", (event) => {
            this.stopGraph()
            console.error(event.data)
        });
    }

    stopWebSocket() {
        this.socket.close()
    }

    onPlayEvent() {

        console.log("play")
        this.listeners = {}
        var listeners = this.listeners
        this.graph.sendEventToAllNodes("connectPublishers", subscribe)
        var data = JSON.stringify(graph.serialize());
        this.startWebSocket(data)

        function subscribe(current_node, source_location, eventId, action) {
            if (!(listeners[eventId.type])) {
                listeners[eventId.type] = []
            }
            if (source_location.position.toLowerCase() == "input") {
                var source_node = current_node.getInputNode(source_location.slot);
            } else if (source_location.position.toLowerCase() == "output") {
                var source_nodes = current_node.getOutputNodes(source_location.slot)
                var filter = "llm_call"
                source_nodes = source_nodes.filter((element) => element.type.endsWith(filter));
                if (source_nodes.length == 1) {
                    var source_node = source_nodes[0]
                }
            }

            var shouldAbort = false
            if (source_node) {
                eventId.source = source_node.id.toString()
            } else {
                shouldAbort = true
            }

            if ((!shouldAbort) && source_location.position.toLowerCase() == "input" && !("slot" in eventId)) {
                var inputLink = current_node.getInputLink(source_location.slot)

                // check direct connections
                if (eventId.type == "output") {
                    eventId.slot = inputLink.origin_slot
                }
                if (eventId.type == "print" && inputLink.origin_slot > 0) {
                    shouldAbort = true
                }

            }

            if (!shouldAbort) {
                var typelistener = listeners[eventId.type]
                typelistener.push([eventId, action_set])
            }
            //console.log(eventId ,callback)
            function action_set(eventId, eventData) {
                current_node.container.executeAction(eventId, action, eventData)
            }
        }




    }

    notifyListeners(eventId, eventData) {
        var typeListeners = this.listeners[eventId.type] || []
        typeListeners = typeListeners.filter(eventFilter)
        typeListeners.map(executeCallback)
        //console.log(eventId, eventData);

        function eventFilter(element) {
            var f1 = eventId.source == element[0].source;
            var f2 = eventId.type == element[0].type;
            var f3 = (!("slot" in element[0])) || (eventId.slot == element[0].slot);
            var res = f1 && f2 && f3;
            return res;
        }

        function executeCallback(element) {
            var callback = element[1]
            callback(eventId, eventData)
        }
    }

    processChunk(buffer, chunk) {
        buffer.text += chunk
        var lines = buffer.text.split("\n")
        buffer.text = lines.pop()
        lines.forEach((element) => {
            if (element.length > 0) {
                this.processMessage(element)
            }
        });

    }



    processMessage(text) {
        var obj = JSON.parse(text);

        if (obj.type == "output") {
            var name = obj.data[0].substr(1)
            var values = obj.data[1]
            var n = this.graph.getNodeById(name)
            if ((!!n) && values.length > 0) {

                for (let i = 0; i < values.length; i++) {
                    var string = new String(values[i]);
                    var value = values[i]
                    string.graphllm_type = "output"
                    string.text_content = values[i]
                    if (value)
                        n.setOutputData(i, string)
                    else
                        n.setOutputData(i, value)

                    var eventId = {
                        type: obj.type,
                        source: name,
                        slot: i
                    }

                    if (value != null) {
                        this.notifyListeners(eventId, values[i])
                    }
                }

            }
        }

        if (obj.type == "print") {
            var name = obj.data[0].split("/")[1]
            var value = obj.data[1]
            var n = this.graph.getNodeById(name)
            if ((!!n) && n.outputs && n.outputs.length > 0) {
                var old = n.print_log || ""
                var newVal = old + value
                n.print_log = newVal
                var string = new String(newVal);
                string.graphllm_type = "print"
                string.text_content = newVal
                n.setOutputData(0, string)

                var eventId = {
                    type: obj.type,
                    source: name
                }
                this.notifyListeners(eventId, value)
            }
        }

        if (obj.type == "error") {
            var message = "error: " + obj.data[0]
            console.log(message)
            alert(message)
        }
        if (obj.type == "request") {
            if (obj.subtype == "audio") {
                var ref = obj.address
                ref = "/blob/" + ref
                console.log(ref)
                this.audio.src = ref
                this.audio.load();
                var req_id = obj.id
                var socket = this.socket
                this.audio.onended = function() {
                    console.log("play ended");
                    socket.send(JSON.stringify({
                        type: "response",
                        subtype: "audio",
                        id: req_id
                    }))
                };
                this.audio.onerror = function() {
                    console.log("play error");
                    //avoid duplicate response: socket.send( JSON.stringify({type: "response", subtype: "audio", id: req_id}))
                };
                this.audio.play().then(_ => {
                    console.log("play started")
                }).catch((error) => {
                    socket.send(JSON.stringify({
                        type: "response",
                        subtype: "audio",
                        id: req_id
                    }))
                    console.error(error);
                });;

            }

            if (obj.subtype == "call") {
                var name = obj.data[0].substr(1)
                var node = this.graph.getNodeById(name)
                var result = {}
                if (node) {
                    try {
                        result = this.bridge_node.node_call(node, obj.data[1], obj.data[2])

                    } catch (error) {
                        console.error(error);
                        alert(error)
                        this.stopGraph()
                    }
                }
                this.socket.send(JSON.stringify({
                    type: "response",
                    subtype: "audio",
                    id: obj.id,
                    data: result
                }))
                //

            }

        }


        if (obj.type == "running") {
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
        if (obj.type == "starting") {
            var name = obj.data[0].split("/")[1]
            var node = this.graph.getNodeById(name)
            if (node) {
                if (!node.is_selected) {
                    this.canvas.selectNode(node, true);
                }
                if (node.outputs && node.outputs.length > 0) {
                    node.print_log = ""
                }
                var eventId = {
                    type: obj.type,
                    source: name
                }
                this.notifyListeners(eventId)
            }

        }

        if (obj.type == "async_call") {
            var name = obj.data[0].split("/")[1]
            var node = this.graph.getNodeById(name)
            var result = {}
            if (node) {
                try {
                    result = this.bridge_node.node_call(node, obj.data[1], obj.data[2])
                } catch (error) {
                    console.error(error);
                    alert(error)
                    this.stopGraph()
                }
            }

        }

        if (obj.type == "node_assign") {
            var name = obj.data[0].split("/")[1]
            var node = this.graph.getNodeById(name)
            var result = {}
            if (node) {
                try {
                    result = this.bridge_node.node_assign(node, obj.data[1], obj.data[2])
                } catch (error) {
                    console.error(error);
                    alert(error)
                    this.stopGraph()
                }
            }

        }

        if (obj.type == "stopping") {
            var name = obj.data[0].substr(1)
            var node = this.graph.getNodeById(name)
            if (node) {
                this.canvas.deselectNode(node);
                var eventId = {
                    type: obj.type,
                    source: name
                }
                this.notifyListeners(eventId)
            }
        }


        if (obj.type != "print") {
            console.log(text, '\n');
        }
    }

    onStopEvent() {
        this.stopWebSocket()

        this.audio.pause()
        console.log("stop")
        this.canvas.selectNodes([])
    }

    onAfterStep() {
        if (this.cb_as)
            this.cb_as();
    }

    onSerialize(data) {
        // groups
        var group_states = new Object()
        for (let el in data.groups) {
            var group = this.graph._groups[el]
            if ("collapse_state" in group) {
                group_states[el] = group.collapse_state
            }
        }
        data["group_states"] = group_states

        // graph name
        var e = this.nameSelector
        var selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text
        var value = selectedFolder + "/" + e.value;
        data["graph_name"] = value

        //nodes
        var node_states = new Object()
        for (let i in data.nodes) {
            var node_id = data.nodes[i].id
            var node = this.graph.getNodeById(node_id)
            var rotation = node.node_rotation || 0;
            node_states[node_id] = {
                rotation: rotation
            }

        }
        data["node_states"] = node_states

    }

    onDeserialize(data) {
        if ("group_states" in data) {
            for (let el in data.group_states) {
                var group = this.graph._groups[el]
                group.collapse_state = data.group_states[el]
            }

        }
        for (var i = 0; i < this.graph._groups.length; ++i) {
            var group = this.graph._groups[i];
            this.graph_handler.recomputeInsideNodes(group)
        }

        if ("node_states" in data) {
            for (let node_id in data.node_states) {
                var node = this.graph.getNodeById(node_id)
                var info = data.node_states[node_id]
                this.setNodeRotation(node, info.rotation)
            }

        }
        /*
        for (var i = 0; i < this.graph._nodes.length; ++i) {
            var node = this.graph._nodes[i];
            this.graph_handler.recomputeOutsideGroup(node)
        }*/
    }

    startGraph() {
        var isStopped = (graph.status == LGraph.STATUS_STOPPED)
        if (isStopped) {
            this.editor.onPlayButton();
        }
    }

    stopGraph() {
        var wasRunning = (graph.status != LGraph.STATUS_STOPPED);
        if (wasRunning) {
            this.editor.onPlayButton();
        }
        this.graph.stop(); // per sicurezza
        if (wasRunning) {
            this.graph.runStep();
        }
    }

    save() {
        var e = this.nameSelector
        var selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text
        var value = selectedFolder + "/" + e.value;
        var data = JSON.stringify(graph.serialize());
        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/graph/save?file=' + value, false);
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.send(data);
        console.log("save called")
        this.loadList()
    }

    deleteFile() {
        //this.graph.clear()
        var e = this.nameSelector
        var selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text
        var value = selectedFolder + "/" + e.value;
        var data = JSON.stringify(graph.serialize());
        let xhr = new XMLHttpRequest();
        xhr.open('POST', '/graph/delete?file=' + value, false);
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
        var selectedFolder = this.select_folder.options[this.select_folder.selectedIndex].text
        var value = selectedFolder + "/" + e.value;

        let xhr = new XMLHttpRequest();
        xhr.open('GET', '/graph/load?file=' + value, false);
        xhr.addEventListener("error", (event) => {
            alert("server error")
        });
        xhr.setRequestHeader("Content-Type", "application/json")
        xhr.send();
        var data = xhr.responseText
        if (data)
            var parsed = JSON.parse(data)
        if (parsed && parsed.nodes) {
            var registered_types = LiteGraph.registered_node_types
            var registered_basetypes = {}
            for (var key in registered_types) {
                var baseName = key.split("/").reverse()[0]
                registered_basetypes[baseName] = key
            }
            var nodes = parsed.nodes
            var missing_nodes = nodes.filter(function(element) {
                return !(element.type in registered_types)
            });
            missing_nodes.map(function(element) {
                element.type = registered_basetypes[element.type.split("/").reverse()[0]]
            })

        }
        graph.configure(parsed);
        window.setTimeout(graph.change.bind(graph))
        console.log("load called")
    }

    onGuiAction(node, action_name, args) {
        //console.log(node, action_name,args)

        // TODO: enqueue the action events and dequeue .
        // cannot handle immediately because the addinput callback is called before the node is fully constructed

        function responseCB(el){
            el.data.unshift("/" + node.id)
            this.processMessage(JSON.stringify(el))


        }


        window.setTimeout( (e) => { 
								this.bridge_node.enqueueGuiEvent(node, action_name, args, responseCB.bind(this))
							} 
						)
    }

    loadBackup() {
        var data = localStorage.getItem("litegraphg demo backup");
        if (!data)
            return;
        var graph_data = JSON.parse(data);
        this.graph.configure(graph_data);
        if ("graph_name" in graph_data) {
            var e = this.nameSelector;
            let path_split = graph_data["graph_name"].split("/")
            e.value = path_split[path_split.length - 1]

            let folder_option = Array.from(this.select_folder.options).filter((el) => el.value == path_split[0]);
            folder_option = folder_option.length > 0 ? folder_option[0] : null;
            if (folder_option == null) {
                folder_option = document.createElement('option');
                folder_option.value = path_split[0];
                folder_option.innerHTML = path_split[0];
                this.select_folder.appendChild(folder_option);
            }
            folder_option.selected = true
        }
    }
}

const web_bridge = new WebBrige();
web_bridge.connect()
web_bridge.loadBackup()
web_bridge.loadList()

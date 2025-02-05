(function(global) {

        var LiteGraph = global.LiteGraph;
        /* ********************** *******************
                WatchNodeGui: Watch
         ********************** *******************  */
        //node constructor class

        function GroupNodeGui()
        {
            this.flags = {pinned: true}
            this.bgcolor = "#45453580"
            this.shape = LiteGraph.BOX_SHAPE
            this._nodes = []
            this.collapse_state = { is_collapsed: false, node_info: {}}
            this.properties = {collapse_state: this.collapse_state}
            Object.defineProperty(this, '_bounding', {
                get() {
                 var node_bounding = new Float32Array(4)
                 this.getBounding(node_bounding,true)
                return node_bounding
                }
            });
            var pos = [0,0];
            var that = this
            const handler = {
              get(obj, prop) {

                return obj[prop]
              },
              set(obj, prop,val) {
                let delta = val - obj[prop]
                obj[prop] = val

                if ( prop == 1)
                {
                    var x = 0;
                    var y = delta;
                }
                else
                {
                    var x = delta;
                    var y = 0;
                }
                that.processNodeMoved(x,y)
              },
            };


            var ppos = new Proxy(pos,handler)
            Object.defineProperty(this, 'pos', {
                get() {
                    return ppos;
                },

                set(v) {
                    ppos[0] = v[0]
                    ppos[1] = v[1]
                },
                enumerable: true
            });
            this.processNodeMoved = processNodeMoved;
        }

        function processNodeMoved(x,y)
        {
            //console.log(x,y)
            if(!this.graph)
		return;
            var canvas = this.graph.list_of_graphcanvas[0]

            for (var i = 0; i < this._nodes.length; ++i) {

                    var node = this._nodes[i]
                    if(canvas.node_dragged && node.is_selected)
                    {
                        //console.log("boh")
                    }
                    else
                    {
                        node.pos[0] += x
                        node.pos[1] += y
                        }
                    }
        }

        GroupNodeGui.prototype.onAdded = function(graph)
        {
            graph.sendActionToCanvas("sendToBack", [this])
            //this.graph = graph

        }
        GroupNodeGui.prototype.onConfigure = function(info)
        {
            this._nodes = []
            this.collapse_state = info.properties.collapse_state
            this.properties = {collapse_state: this.collapse_state}
            console.log("group restore")

            if(this.flags.collapsed)
            {
                for(let el in this.collapse_state.node_info)
                {
                    var node = this.graph.getNodeById(el)
                    node.onDrawCollapsed = function(){return true;}
                    graph.sendActionToCanvas("sendToBack", [node])
                    node.parent_group = this
                    this._nodes.push(node);
                }

            }
            else
            {
                for(let el in this.collapse_state.node_info)
                {
                    var node = this.graph.getNodeById(el)
                    node.parent_group = this
                    this._nodes.push(node);
                }
            }
        }

        GroupNodeGui.prototype.recomputeInsideNodes = function(){
            if(!this.flags.collapsed)
            {
                LGraphGroup.prototype.recomputeInsideNodes.apply(this)
            }
        }

        GroupNodeGui.prototype.onDblClick = function ( e, pos, canvas )
        {
            this.collapse()
        }


        GroupNodeGui.prototype.onNodeMoved = function(dragged)
        {
            this.recomputeInsideNodes()
        }

        GroupNodeGui.prototype.onSelected = function()
        {
            if(!this.flags.collapsed)
            {
                this.recomputeInsideNodes()
            }
            //var canvas = this.graph.list_of_graphcanvas[0]
            //canvas.selectNodes(this._nodes)

        }

        GroupNodeGui.prototype.alignToGrid = function()
        {
            LGraphNode.prototype.alignToGrid.apply(this)
            for (var i = 0; i < this._nodes.length; ++i) {
                var n = this._nodes[i]
                    n.alignToGrid();
            }

        }

        GroupNodeGui.prototype.collapse = function(force) {
            var group = this;

            if(!this.flags.collapsed)
            {
                group.collapse_state.node_info = {};
                for (var i = 0; i < this._nodes.length; ++i) {
                    var node = this._nodes[i]
                    var delta_pos = [ node.pos[0] - group.pos[0],  node.pos[1] - group.pos[1]]
                    var new_pos = [ group.pos[0] + 0,   group.pos[1] + 0]
                    group.collapse_state.node_info[node.id] = {id: node.id, size: node.size, pos: delta_pos, collapsed: node.flags.collapsed}
                    if(!node.flags.collapsed)
                    {
                        node.collapse(force)
                        graph.sendActionToCanvas("sendToBack", [node])
                    }
                    node.pos = new_pos
                    node.onDrawCollapsed = function(){return true;}
                }
				LGraphNode.prototype.collapse.apply(this,force)
            }
            else
            {
                for (var i = 0; i < this._nodes.length; ++i) {
                    var node = this._nodes[i]
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
                    node.onDrawCollapsed = null
                }
				
				var collapsed_size = [ this._collapsed_width, LiteGraph.NODE_TITLE_HEIGHT]
				var center_pos  = [this.pos[0] + collapsed_size[0]/2, this.pos[1] + collapsed_size[1]/2]
				
				LGraphNode.prototype.collapse.apply(this,force)
				
				// push away overlapping nodes
				for (var i = 0; i < this.graph._nodes.length; ++i) {
                    var node = this.graph._nodes[i]
					var id = '' + node.id
					var node_bounding = new Float32Array(4);
					node.getBounding(node_bounding,true);
					if (!LiteGraph.overlapBounding(this._bounding, node_bounding)) {
						continue;
					}
					if(Object.keys(group.collapse_state.node_info).includes(id))
					{
						continue;
					}
					if(node == this)
					{
						continue;
					}
					if (node.constructor.name == "GroupNodeGui" && !node.flags.collapsed)
					{
						node.collapse() 
					}
					
					
					// push the other node along the line connecting centers. assuming distance[0] and 1 are positive
					var other_size = [node.size[0], node.size[1] + LiteGraph.NODE_TITLE_HEIGHT]
					var other_pos = [node.pos[0] + other_size[0]/2, node.pos[1] + other_size[1]/2]
					var center_distance = [other_pos[0] - center_pos[0], other_pos[1] - center_pos[1]]
					var distance_required = [this.size[0] + other_size[0]/2 + 10 - collapsed_size[0]/2,
					                          (this.size[1]+ LiteGraph.NODE_TITLE_HEIGHT) + other_size[1]/2 + 10 - collapsed_size[1]/2]
					var tentativey = center_distance[1] * distance_required[0]/center_distance[0]
					var tentativex = distance_required[0]
					
					if (tentativey > distance_required[1])
					{
						tentativey = distance_required[1]
						tentativex = center_distance[0] * distance_required[1]/center_distance[1]
					}
					
					node.pos[0] += tentativex - center_distance[0]
					node.pos[1] += tentativey - center_distance[1]

					

				}
				
                graph.sendActionToCanvas("sendToBack", [this])
            }
            
        }

        GroupNodeGui.prototype.onConnectionsChange = function(dir,slot,connected,d,e)
        {
            console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )

        }

        GroupNodeGui.title = "Group"
        LiteGraph.registerNodeType("graph/group", GroupNodeGui );


        })(this);


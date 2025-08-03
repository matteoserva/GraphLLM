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

        function setCollapsedWidth(group, child)
        {
                try {
                       Object.defineProperty(child, "_collapsed_width", {
                        configurable: true,
                        set : function (value) {child.__collapsed_width = value},
                        get : function () {return group._collapsed_width}
                        });
                    } catch {}

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

                    setCollapsedWidth(this,node)
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
            console.log("group collapsed",this.flags.collapsed)
            if(!this.flags.collapsed)
            {
                group.collapse_state.node_info = {};
                for (var i = 0; i < this._nodes.length; ++i) {
                    var node = this._nodes[i]
                    var delta_pos = [ node.pos[0] - group.pos[0],  node.pos[1] - group.pos[1]]
                    let offset_y = LiteGraph.NODE_TITLE_HEIGHT * (1+i)
                    var new_pos = [ group.pos[0] + 0,   group.pos[1] + offset_y]
                    group.collapse_state.node_info[node.id] = {id: node.id, size: node.size, pos: delta_pos, collapsed: node.flags.collapsed}
                    if(!node.flags.collapsed)
                    {
                        node.collapse(force)
                    }
					
                    console.log("add collapse: ", node.getTitle())
                    setCollapsedWidth(this,node)

                    node.pos = new_pos
                    //node.onDrawCollapsed = function(){return true;}
                }

				LGraphNode.prototype.collapse.apply(this,force)
				graph.sendActionToCanvas("bringToFront", [this])
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

                    //node.onDrawCollapsed = function(){return true;}
                    delete node._collapsed_width
                    console.log("detete collapse: ", node.getTitle())
                    //node.onDrawCollapsed = null
                }
				

				var group_bonding = group._bounding
				var center_pos  = [group_bonding[0] + group_bonding[2]/2, group_bonding[1] + group_bonding[3]/2]
				LGraphNode.prototype.collapse.apply(this,force)
				push_away(this, center_pos, this.graph)

				
                graph.sendActionToCanvas("sendToBack", [this])
            }
            console.log("now collapsed",this.flags.collapsed)
        }

        function push_away(group, center_pos, graph)
        {
				var group_bonding = new Float32Array(4);
				group.getBounding(group_bonding,true)
				var pushed_nodes = []
        // push away overlapping nodes
				for (var i = 0; i < group.graph._nodes.length; ++i) {
                    var node = group.graph._nodes[i]
					var id = '' + node.id
					var node_bounding = new Float32Array(4);
					node.getBounding(node_bounding,true);
					if (!LiteGraph.overlapBounding(group_bonding, node_bounding)) {
						continue;
					}
					if(group.constructor.name == "GroupNodeGui" && Object.keys(group.collapse_state.node_info).includes(id))
					{
						continue;
					}
					if(node == group)
					{
						continue;
					}
					if (node.constructor.name == "GroupNodeGui" && !node.flags.collapsed)
					{
						node.collapse()
                        node.getBounding(node_bounding,true);
                        if (!LiteGraph.overlapBounding(group_bonding, node_bounding)) {
                            continue;
                        }
					}

					// push the other node along the line connecting centers. assuming distance[0] and 1 are positive
					var other_size = [node_bounding[2], node_bounding[3]]
					var center_other = [node_bounding[0] + node_bounding[2]/2, node_bounding[1] + node_bounding[3]/2]
					var center_distance = [center_other[0] - center_pos[0], center_other[1] - center_pos[1]]

                    var other_minimum_delta = [0,0]
                    if (center_distance[0] > 0)
                    {
                        other_minimum_delta[0] = group_bonding[0] + 1 + group_bonding[2] - node_bounding[0]
                    }
                    else
                    {
                        other_minimum_delta[0] = group_bonding[0] -1 - (node_bounding[0] + node_bounding[2])
                    }

                    if (center_distance[1] > 0)
                    {
                        other_minimum_delta[1] = group_bonding[1] + 1 +group_bonding[3] - node_bounding[1]
                    }
                    else
                    {
                        other_minimum_delta[1] = group_bonding[1] - 1 -(node_bounding[1] + node_bounding[3])
                    }
                    var tentativex = other_minimum_delta[0]
                    var tentativey = tentativex * center_distance[1] / center_distance[0]

                    if ((center_distance[1] > 0 && tentativey > other_minimum_delta[1]) || (center_distance[1] < 0 && tentativey < other_minimum_delta[1]))
                    {
                        tentativey = other_minimum_delta[1]
                        tentativex = tentativey * center_distance[0] / center_distance[1]
                    }

					node.pos[0] += tentativex
					node.pos[1] += tentativey

                    pushed_nodes.push({node: node, center: center_other})

				}
				for(i in pushed_nodes)
				{
				    var el = pushed_nodes[i]
				    //console.log("pushed: ", el)
				    push_away(el.node,el.center,graph)
				}
        }


        GroupNodeGui.prototype.isPointInside = function(x, y, margin, skip_title) {
            if(!this.flags.collapsed)
            {
                return  LGraphNode.prototype.isPointInside.call(this, x, y, margin, skip_title);
            }

            return LiteGraph.isInsideRectangle(
                    x,
                    y,
                    this.pos[0] - margin,
                    this.pos[1] - LiteGraph.NODE_TITLE_HEIGHT - margin,
                    (this._collapsed_width || LiteGraph.NODE_COLLAPSED_WIDTH) +
                        2 * margin,
                    LiteGraph.NODE_TITLE_HEIGHT + 2 * margin + LiteGraph.NODE_TITLE_HEIGHT*this._nodes.length
                )
        };

        GroupNodeGui.prototype.getExtraMenuOptions = function (canvas,options)
        {
            var menu_info = canvas.getCanvasMenuOptions();
            //menu_info = canvas.getNodeMenuOptions({})
            menu_info = [
                {
                    content: "Add Node",
                    has_submenu: true,
                    callback: onMenuAdd
                }
                ]
            return menu_info;

            function onMenuAdd(node, options, e, prev_menu, callback)
            {
                LGraphCanvas.onMenuAdd(node, options, e, prev_menu, null)
            }
        }

        GroupNodeGui.prototype.onConnectionsChange = function(dir,slot,connected,d,e)
        {
            console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )

        }

        GroupNodeGui.prototype.onDrawCollapsed = function(ctx,canvas)
        {
            let node = this;
            var color = node.color || node.constructor.color || LiteGraph.NODE_DEFAULT_COLOR;
            var bgcolor = node.bgcolor || node.constructor.bgcolor || LiteGraph.NODE_DEFAULT_BGCOLOR;

            let size = new Float32Array(2);


            size.set(node.size)
            {
                ctx.font = this.inner_text_font;
                var title = node.getTitle ? node.getTitle() : node.title;
                {
                    let maxWidths= node._nodes.map((el) => el.__collapsed_width)

                    let _collapsed_width = Math.min(
                        node.size[0],
                        ctx.measureText(title).width +
                            LiteGraph.NODE_TITLE_HEIGHT * 2
                    ); //LiteGraph.NODE_COLLAPSED_WIDTH;
                    maxWidths.push(_collapsed_width)
                    node._collapsed_width = Math.max(...maxWidths)
                    size[0] = node._collapsed_width;
                    size[1] = LiteGraph.NODE_TITLE_HEIGHT*this._nodes.length;
                }
            }
            canvas.drawNodeShape(
                node,
                ctx,
                size,
                color,
                bgcolor,
                node.is_selected,
                node.mouseOver
            );
            return true;
        }

        GroupNodeGui.title = "Group"
        LiteGraph.registerNodeType("graph/group", GroupNodeGui );


        })(this);


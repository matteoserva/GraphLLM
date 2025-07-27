class GraphHandler {
    constructor(graph,canvas)
    {
        this.graph = graph
        this.canvas = canvas
    }

    connect()
    {
		this.canvas.onMouse = this.processMouseDownPre.bind(this)
        this.canvas.onMouseDown = this.processMouseDown.bind(this)
        this.canvas.onNodeMoved = this.onNodeMoved.bind(this)
		this.canvas.onRender = this.onRender.bind(this)
		this.canvas.onDrawForeground = this.onDrawForeground.bind(this)
        LiteGraph.pointerListenerAdd(document,"up", this.processMouseUp.bind(this),true);
        LiteGraph.addNodeMethod("getConnectionPos",this.over_getConnectionPos)
        //LiteGraph.addNodeMethod("addInput" ,this.over_addInput)
        let that = this
        LiteGraph.addNodeMethod("onInputAdded" , function(connection){return that.onConnectionAdded(this,connection,LiteGraph.LEFT)})
        LiteGraph.addNodeMethod("onOutputAdded" , function(connection){return that.onConnectionAdded(this,connection,LiteGraph.RIGHT)})


        var orig = LGraphGroup.prototype.recomputeInsideNodes
        LGraphGroup.prototype.recomputeInsideNodes = function() {
            var group = this
            that.recomputeInsideNodes(group,orig)
        };


    }

  onConnectionAdded(node,connection, default_value)
  {
     let dir = connection.dir || default_value
        /*UP: 1,
        DOWN: 2,
        LEFT: 3,
        RIGHT: 4,
        CENTER: 5,*/
     Object.defineProperty(connection, "dir", {
                                    get: function() {
                                        let x = dir
                                        if(node.horizontal) x = [1,4,3,1,2][x]
                                        if(node.flipped) x = [4,2,1,4,3][x]
                                        return x
                                    },
                                    configurable: true,
                                    set: function(v) {
                                         dir = v
                                    },
                                });

     return connection;
  }

  over_getConnectionPos(is_input,       slot_number,        out)
  {
    let o = this._getConnectionPos(is_input,       slot_number,        out);
    if(this.flipped)
    {
        if(this.horizontal)
        {
            o[1] = this.pos[1] + this.size[1] - (o[1] + LiteGraph.NODE_TITLE_HEIGHT - this.pos[1])
        }
        else
        {
            o[0] = this.pos[0] + this.size[0] + 1 - ( o[0] - this.pos[0])
        }
    }
    return o
  }

  onRender(canvas, ctx){ // after background, before nodes
	//console.log("onrender")
	
  }
  onDrawForeground(ctx, visible_rect)
  {
	 var visible_nodes = this.canvas.visible_nodes
	 var all_nodes = this.graph._nodes;
	 var hidden_nodes = all_nodes.filter((el) => !visible_nodes.includes(el));
	 hidden_nodes.map((el) => {if (el.onVisibilityChange) {
		 el.onVisibilityChange.map((f) => f(false));
		 
		 }});
	 visible_nodes.map((el) => {if (el.onVisibilityChange) {
		 el.onVisibilityChange.map((f) => f(true));
		 
		 }});
	 
  }

  onNodeMoved(node_dragged)
  {
    //console.log("dragged")
  }

  processMouseDownPre(e)
  {
	if(this.canvas.pointer_is_double) 
	{
		this.canvas.adjustMouseEvent(e);
		var mouse = [e.clientX, e.clientY];
		this.canvas.block_click = true;
		//alert("val1: " + this.canvas.last_mouse + "   val2: " + mouse) 

		this.canvas.pointer_is_double = false;
		return true;
	}
	  
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
	
	//workaround on mobile, don't open the context menu while dragging with two fingers
	/*if(this.canvas.pointer_is_double) 
	{
		var ref_window = this.canvas.getCanvasWindow();
		LiteGraph.closeAllContextMenus(ref_window);
	}*/

  }

  groupCollapse(group)
  {
        for (var i = 0; i < group._nodes.length; ++i) {
            var node = group._nodes[i];
            var delta_pos = [ node.pos[0] - group.pos[0],  node.pos[1] - group.pos[1]]
            var new_pos = [ group.pos[0] + 20,   group.pos[1] + 70]
            group.collapse_state.node_info[node.id] = {id: node.id, size: node.size, pos: delta_pos, collapsed: node.flags.collapsed}

            node.pos = new_pos
            if(!node.flags.collapsed)
            {
                node.collapse()
            }



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

  groupExpand(group)
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

        // check overlaps with other expanded groups
        for (var i = 0; i < this.graph._groups.length; ++i) {
            var other = this.graph._groups[i]
            if(other == group)
            {
                continue;
            }
            if (!LiteGraph.overlapBounding(group._bounding, other._bounding)) {
                continue;
            }
            if (other.collapse_state && !other.collapse_state.is_collapsed)
            {
                this.groupCollapse(other)
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

        if(is_double_click)
        {
            if(this.canvas.node_dragged && this.canvas.node_dragged.onDblClick)
            {
                this.canvas.node_dragged.onDblClick();
            }
        }
		
		//workaround on mobile, open the right click menu if tapping with second finger
		var is_secondary = e.isPrimary === false;
		if(is_secondary)
		{
			// is it hover a node ?
			var node = null;
			/*if (node){
				if(Object.keys(this.selected_nodes).length
				   && (this.selected_nodes[node.id] || e.shiftKey || e.ctrlKey || e.metaKey)
				){
					// is multiselected or using shift to include the now node
					if (!this.selected_nodes[node.id]) this.selectNodes([node],true); // add this if not present
				}else{
					// update selection
					this.selectNodes([node]);
				}
			}
			*/
			// show menu on this node
			this.canvas.processContextMenu(node, e);
			//alert("is secondary")
		}

        if(this.canvas.selected_group)
        {
            this.recomputeInsideNodes(this.canvas.selected_group)

        }
        if (this.canvas.align_to_grid && this.canvas.resizing_node)
        {
            this.canvas.resizing_node.size[0] = LiteGraph.CANVAS_GRID_SIZE * Math.round(this.canvas.resizing_node.size[0] / LiteGraph.CANVAS_GRID_SIZE);
            this.canvas.resizing_node.size[1] = LiteGraph.CANVAS_GRID_SIZE * Math.round(this.canvas.resizing_node.size[1] / LiteGraph.CANVAS_GRID_SIZE);
        }

        if(this.canvas.node_dragged || this.canvas.resizing_node)
        {
            let node = this.canvas.node_dragged || this.canvas.resizing_node
            this.recomputeOutsideGroup(node)

            if (node.constructor.name == "GroupNodeGui")
            {
                node.recomputeInsideNodes()
            }
        }

        if(should_handle)
        {
            var group = this.canvas.selected_group
            if (group.collapse_state === undefined)
            {
                group.collapse_state = { is_collapsed: false, node_info: new Object()}
            }
            if (group.collapse_state.is_collapsed)
            {
                this.groupExpand(group)
                //
            }
            else
            {
                this.groupCollapse(group)

            }
        }
        //console.log("group: " + this.canvas.selected_group + "   double " + is_double_click + "   time: "
        //+ (now - this.canvas.last_mouseclick), " p " + this.previousClick + "  t " + [total,t1,t2])

    return false;
  }

   recomputeOutsideGroup(node)
  {
    var node_bounding = new Float32Array(4);
    node.getBounding(node_bounding);

    if (node.parent_group)
    {
        if (LiteGraph.overlapBounding(node.parent_group._bounding, node_bounding)) {
            return;
        }

    }

    var found_group = null
    for (var i = 0; i < this.graph._groups.length; ++i) {
        var group = this.graph._groups[i]
        if (!LiteGraph.overlapBounding(group._bounding, node_bounding)) {
            continue;
        }
        found_group = group
    }

    if (node.constructor.name != "GroupNodeGui")
    {
        for (var i = 0; i < this.graph._nodes.length; ++i) {
            var group = this.graph._nodes[i];
            if(group == node)
            {
                continue;
            }
            if (group.constructor.name != "GroupNodeGui")
            {
                continue
            }
            if (!LiteGraph.overlapBounding(group._bounding, node_bounding)) {
                continue;
            }
            if (group.flags.collapsed)
            {
                continue
            }
            found_group = group
        }
    }

    if (found_group)
    {
        if(node.parent_group && node.parent_group._nodes)
        {
            deleteByValue(node.parent_group._nodes, node)
        }
        if(found_group._nodes)
        {
            deleteByValue(found_group._nodes, node)
            found_group._nodes.push(node)
        }



        node.parent_group = found_group

        function deleteByValue(obj, val) {
            var index = obj.indexOf(val);
            if (index !== -1) {
              obj.splice(index, 1);
            }
        }




    }
    else
    {
        node.parent_group = null
    }

  }

  recomputeInsideNodes(group, orig)
  {
    group._nodes.length = 0;
    var nodes = this.graph._nodes;
    var node_bounding = new Float32Array(4);

    for (var i = 0; i < nodes.length; ++i) {
        var node = nodes[i];
        node.getBounding(node_bounding);
        if(node == group)
        {
            continue;
        }
        if (group.constructor.name == "GroupNodeGui" && node.constructor.name == "GroupNodeGui")
        {
            continue;
        }

        if (!LiteGraph.overlapBounding(group._bounding, node_bounding)) {
            continue;
        } //out of the visible area
        if(node.parent_group && node.parent_group != group)
        {
            var parent_group = node.parent_group
            if (group.constructor.name == "GroupNodeGui" && node.parent_group.constructor.name != "GroupNodeGui")
            {

                console.log("stealing")
            }
            else
            {
                if (LiteGraph.overlapBounding(parent_group._bounding, node_bounding)) {
                continue;
                }
            }


        }
        group._nodes.push(node);
        node.parent_group = group
    }

  }
}
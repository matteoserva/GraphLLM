(function(global) {

    var LiteGraph = global.LiteGraph;


    //node constructor class
    function MyGraphNode()
    {
    this.addInput("in","string");

    this.addOutput("out","string");

    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.properties = {  };
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})


    }

    //name to show
    MyGraphNode.title = "Generic node";

    //function to call when the node is executed
    MyGraphNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    if( A === undefined )
        A = 0;
    var B = this.getInputData(1);
    if( B === undefined )
        B = 0;

    }

    MyGraphNode.prototype.onStart = function()
    {
        console.log("started")

    }

    function connectionChangeInner ( node, dir,slot,connected,d,e)
    {
        console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )
		let gui_node_config = node.gui_node_config || {}
		let connection_limits = gui_node_config.connection_limits || {}
		var saved_size = node.size
        if(dir == LiteGraph.INPUT)
        {
              if(connected)
              {
                  let should_add = true
                  if( connection_limits.max_inputs && node.inputs.length >= connection_limits.max_inputs)
                  {
                     should_add = false
                  }

                  if( should_add && node.inputs.length <= (slot +1) && !!d)
                  {
                    node.addInput("N","string");
                  }
              }
              else
              {
                    let numInputs = node.inputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numInputs; i++) {
                        if(!!node.inputs[i].link)
                        {
                            maxInput = i
                        }
                    }
                    maxInput = 1+ maxInput
                    if( connection_limits.min_inputs)
                    {
                        maxInput = Math.max(maxInput, connection_limits.min_inputs-1 )
                    }
                    for (let i = numInputs-1; i > maxInput; i--) {
                            node.removeInput(i)
                    }
                }
        }
        if(dir == LiteGraph.OUTPUT)
        {
              if(connected)
              {
                  let numElements = node.outputs.length
                  let should_add = true
                  if( connection_limits.max_outputs && numElements >= connection_limits.max_outputs)
                    should_add = false

                  if(slot +1 == numElements && !!d && should_add)
                  {
                    node.addOutput("N","string");
                  }
              }
              else
              {
                    let numElements = node.outputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numElements; i++) {
                        if((!!node.outputs[i].links) && node.outputs[i].links.length > 0)
                        {
                            maxInput = i
                        }
                    }
                     for (let i = numElements-1; i > maxInput+1; i--) {
                            node.removeOutput(i)
                    }

               }
        }
        node.size[0] = saved_size[0]
        node.size[1] = Math.max(node.size[1],saved_size[1])
    }

    function inputMirrorInner(node, dir,slot,connected,d,e)
    {
        console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )
		let gui_node_config = node.gui_node_config || {}
		let connection_limits = gui_node_config.connection_limits || {}
		var saved_size = node.size
        if(dir == LiteGraph.INPUT)
        {
              if(connected)
              {
                  while( node.inputs.length <= (slot +1)  && !!d)
                  {
                    node.addInput("N","string");
                  }

                  while( node.outputs.length <= (slot)  && !!d)
                  {
                    node.addOutput("N","string");
                  }
              }
              else
              {
                    let numInputs = node.inputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numInputs; i++) {
                        if(!!node.inputs[i].link)
                        {
                            maxInput = i
                        }
                    }
                    maxInput = 1+ maxInput
                    if( connection_limits.min_inputs)
                    {
                        maxInput = Math.max(maxInput, connection_limits.min_inputs-1 )
                    }
                    for (let i = numInputs-1; i > maxInput; i--) {
                            node.removeInput(i)
                    }
                    maxOutput = maxInput - 1
                    for (let i = node.outputs.length-1; i > maxOutput; i--) {
                            node.removeOutput(i)
                    }
                }
        }

        node.size[0] = saved_size[0]
        node.size[1] = Math.max(node.size[1],saved_size[1])
    }

    MyGraphNode.prototype.onConnectionsChange = function(...args)
    {
        let node = this
        setTimeout(function(){
                        return connectionChangeInner(node, ...args)
                    }
                  );
    }

    MyGraphNode.prototype.mirrorInputs = function(dir,slot,connected,d,e)
    {
        let node = this
        return inputMirrorInner(node, dir,slot,connected,d,e)
    }


    window.MyGraphNode = MyGraphNode
})(this);
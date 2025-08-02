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

    MyGraphNode.prototype.onConnectionsChange = function(dir,slot,connected,d,e)
    {
        console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )
		let gui_node_config = this.gui_node_config || {}
		let connection_limits = gui_node_config.connection_limits || {}
        if(dir == LiteGraph.INPUT)
        {
              if(connected)
              {
                  let numInputs = this.inputs.length
                  if(slot +1 == numInputs && !!d)
                  {
                    var saved_size = this.size
                    this.addInput("N","string");
                    this.size[0] = saved_size[0]
                    this.size[1] = Math.max(this.size[1],saved_size[1])
                    //this.setSize( this.computeSize() );
                  }

              }
              else
              {
                    let numInputs = this.inputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numInputs; i++) {
                        if(!!this.inputs[i].link)
                        {
                            maxInput = i
                        }
                    }
                    if( connection_limits.min_inputs)
                    {
                        maxInput = Math.max(1+ maxInput, connection_limits.min_inputs-1 )
                    }
                     for (let i = numInputs-1; i > maxInput; i--) {
                             var saved_size = this.size
                            this.removeInput(i)
                            this.size[0] = saved_size[0]
                            this.size[1] = Math.max(this.size[1],saved_size[1])
                            //this.setSize( this.computeSize() );

                    }
                }
        }
        if(dir == LiteGraph.OUTPUT)
        {
              if(connected)
              {
                  let numElements = this.outputs.length
                  let should_add = true
                  if( connection_limits.max_outputs && numElements >= connection_limits.max_outputs)
                    should_add = false

                  if(slot +1 == numElements && !!d && should_add)
                  {
                    var saved_size = this.size
                    this.addOutput("N","string");
                    this.size[0] = saved_size[0]
                    this.size[1] = Math.max(this.size[1],saved_size[1])

                    //this.setSize( this.computeSize() );
                  }
                  //this.graph.change() //TODO reposition the connection in input/output node when minimized

              }
              else
              {
                setTimeout(function(){ // in case the disconnect is immediately followed by a connect
                    let numElements = this.outputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numElements; i++) {
                        if((!!this.outputs[i].links) && this.outputs[i].links.length > 0)
                        {
                            maxInput = i
                        }
                    }
                     for (let i = numElements-1; i > maxInput+1; i--) {
                            var saved_size = this.size
                            this.removeOutput(i)
                            this.size[0] = saved_size[0]
                            this.size[1] = Math.max(this.size[1],saved_size[1])
                            //this.setSize( this.computeSize() );

                    }
               }.bind(this))
               }
        }
    }



    window.MyGraphNode = MyGraphNode
})(this);
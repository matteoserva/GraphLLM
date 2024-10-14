


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
    this.setSize( this.computeSize() );
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
        //let xhr = new XMLHttpRequest();
        //xhr.open('GET', '/graph/exec',false);
        //xhr.send();
        //console.log(xhr.response);
    //this.setOutputData( 0, xhr.response );
    
    //
    }
    
    MyGraphNode.prototype.onStart = function()
    {
        console.log("started")
   
    }

    MyGraphNode.prototype.onConnectionsChange = function(dir,slot,connected,d,e)
    {
        console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )
        if(dir == LiteGraph.INPUT)
        {
              if(connected)
              {
                  let numInputs = this.inputs.length
                  if(slot +1 == numInputs && !!d)
                  {
                    this.addInput("N","string"); 
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
                     for (let i = numInputs-1; i > maxInput+1; i--) {
                      
                            this.removeInput(i)
                            //this.setSize( this.computeSize() );
                     
                    }
                }
        }
        if(dir == LiteGraph.OUTPUT)
        {
              if(connected)
              {
                  let numElements = this.outputs.length
                  if(slot +1 == numElements && !!d)
                  {
                    this.addOutput("N","string");
                    //this.setSize( this.computeSize() );
                  }

              }
              else
              {
                    let numElements = this.outputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numElements; i++) {
                        if(!!this.outputs[i].link)
                        {
                            maxInput = i
                        }
                    }
                     for (let i = numElements-1; i > maxInput+1; i--) {

                            this.removeOutput(i)
                            //this.setSize( this.computeSize() );

                    }
                }
        }
    }
    
    //register in the system
    LiteGraph.registerNodeType("llm/generic_node", MyGraphNode );

    /* ********************** ******************* */
    //node constructor class
    function MyLLMCallNode()
    {
    this.addInput("in","string");

    this.addOutput("out","string");

    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.addWidget("text","Config","", { property: "conf"});

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.properties = {conf:""  };
    this.container.addWidget("textarea","template",{ property: "template"})
    this.setSize( this.computeSize() );
    }

    //name to show
    MyLLMCallNode.title = "LLM Call";



    MyLLMCallNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange

    //register in the system
    LiteGraph.registerNodeType("llm/llm_call", MyLLMCallNode );



    //node constructor class
    function MyWatchNode()
    {
    this.addInput("in","string");
    
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("textarea","",{ property: "parameters"})
    
    var tmpl = ""
    this.properties = { };
    this.setSize( this.computeSize() );
    }

    //name to show
    MyWatchNode.title = "Watch";

    //function to call when the node is executed
    MyWatchNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    this.container.setValue("parameters",A)
    }

    //register in the system
    LiteGraph.registerNodeType("llm/watch", MyWatchNode );




    //node constructor class
    function MyInputNode()
    {
    this.addOutput("out","string");
    
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    

    this.properties = {  };
    this.setSize( this.computeSize() );
    }

    //name to show
    MyInputNode.title = "Input";





    //register in the system
    LiteGraph.registerNodeType("llm/input", MyInputNode );



    /* ----------------- -------------- */
    //node constructor class
    function MyVirtualSourceNode()
    {
    this.addOutput("out","string");
    this.addWidget("text","identifier","", { property: "identifier"});

    this.properties = { identifier: "" };
    }

    //name to show
    MyVirtualSourceNode.title = "Virtual Source";

    //function to call when the node is executed
    MyVirtualSourceNode.prototype.onExecute = function(){}

    //register in the system
    LiteGraph.registerNodeType("llm/virtual_source", MyVirtualSourceNode );

       /* ----------------- -------------- */
    //node constructor class
    function MyVirtualSinkNode()
    {
    this.addInput("in","string");
    this.addWidget("text","identifier","", { property: "identifier"});

    this.properties = { identifier: "" };
    }

    //name to show
    MyVirtualSinkNode.title = "Virtual sink";

    //function to call when the node is executed
    MyVirtualSinkNode.prototype.onExecute = function(){}

    //register in the system
    LiteGraph.registerNodeType("llm/virtual_sink", MyVirtualSinkNode );



        //node constructor class
    function MyVariableNode()
    {

    this.addWidget("text","identifier","", { property: "identifier"});
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = { identifier: "" };
    }

    //name to show
    MyVariableNode.title = "Variable";

    //register in the system
    LiteGraph.registerNodeType("llm/variable", MyVariableNode );
    
})(this);

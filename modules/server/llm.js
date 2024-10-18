


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
                             var saved_size = this.size
                            this.removeInput(i)
                            this.size[0] = saved_size[0]
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
                    var saved_size = this.size
                    this.addOutput("N","string");
                    this.size[0] = saved_size[0]
                    //this.setSize( this.computeSize() );
                  }

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
                            //this.setSize( this.computeSize() );

                    }
               }.bind(this))
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
    this.properties = {conf:"",subtype:"stateless",template:""  };
    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.addWidget("text","Config","", { property: "conf"});
    this.addProperty("subtype", "stateless", "enum", { values: ["stateless","stateful"]  });
    this.addWidget("combo","subtype","stateless",null, { property: "subtype", values: ["stateless","stateful"] } );
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    
    this.container.addWidget("textarea","template",{ property: "template"})
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
    }

    //name to show
    MyInputNode.title = "Input";

    //register in the system
    LiteGraph.registerNodeType("llm/input", MyInputNode );

    
    /****
     * 
     * 
     * 
     * LIST NODE
     * 
     * */
    function MyListNode()
    {
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("list","Parameters",{ property: "parameters"})
    //this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = {  };
    }

    //name to show
    MyListNode.title = "List";

    //register in the system
    LiteGraph.registerNodeType("llm/list", MyListNode );

        /****
     * 
     * 
     * 
     * LIST NODE
     * 
     * */
    function MyChatHistoryNode()
    {
    this.addOutput("out","string");
    this.addInput("in","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("list","Parameters",{ property: "parameters"})
    //this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = {  };
    }

    //name to show
    MyChatHistoryNode.title = "(NOT WORKING)Chat History";

    //register in the system
    LiteGraph.registerNodeType("llm/chat_history", MyChatHistoryNode );
    
    
    

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


        //node constructor class
    function MyFileNode()
    {
    this.addOutput("out","string");
    this.addInput("in","string");

    this.addWidget("text","filename","", { property: "filename"});
    this.properties = { filename: "" };
    }

    //name to show
    MyFileNode.title = "File";

    //register in the system
    LiteGraph.registerNodeType("llm/file", MyFileNode );
    
})(this);

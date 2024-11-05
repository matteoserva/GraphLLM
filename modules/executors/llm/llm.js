


(function(global) {

    var LiteGraph = global.LiteGraph;




    /*
     *
     *  Python node
     *
     */

    function MyPythonNode()
    {
    this.addInput("in","string");
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);

    this.properties = {  };
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})

    }

    //name to show
    MyPythonNode.title = "Python";

    MyPythonNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange

    //register in the system
    LiteGraph.registerNodeType("tools/python_sandbox", MyPythonNode );



    /* ********************** ******************* */
    //node constructor class
    function MyLLMCallNode()
    {
    this.addInput("in","string");

    this.addOutput("out","string");
    this.properties = {conf:"",subtype:"stateless",template:""  };
    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'


    this.addProperty("subtype", "stateless", "enum", { values: ["stateless","stateful"]  });
    this.addWidget("combo","subtype","stateless",null, { property: "subtype", values: ["stateless","stateful"] } );
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.container.addWidget("text_input","Config",{ property: "conf"})
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
    LiteGraph.registerNodeType("output/watch", MyWatchNode );





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
    MyInputNode.title = "Text Input";

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
    this.addInput("in","string");

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
    var listWidget = this.container.addWidget("list","Parameters",{ property: "parameters"})
    listWidget.makeCellName = function(index)
    {
        if(index == 0)
        {
                return "system";
        }
        else if(index % 2)
        {
                return "user";
        }
        else
        {
                return "assistant"
        }
        return index+1
    }
    listWidget.reset()
    //this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = {  };
    }

    //name to show
    MyChatHistoryNode.title = "Chat History";

    //register in the system
    LiteGraph.registerNodeType("llm/chat_history", MyChatHistoryNode );
    
    MyChatHistoryNode.prototype.onStart = function()
    {
        this.saved_history = JSON.parse(JSON.stringify(this.properties["parameters"]))
        if((this.saved_history.length % 2) != 1)
        {
            this.saved_history.push("")   
        }
    }
    
    MyChatHistoryNode.prototype.onExecute = function()
    {
        var A = this.getInputData(0);
        if( A !== undefined )
        {
            var new_history = JSON.parse(JSON.stringify(this.saved_history))
            var message_index = new_history.length-1
            new_history[message_index] =this.saved_history[message_index] + A
            this.container.setValue("parameters",new_history)
        }
    }
    

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
    LiteGraph.registerNodeType("graph/virtual_source", MyVirtualSourceNode );

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
    LiteGraph.registerNodeType("graph/virtual_sink", MyVirtualSinkNode );



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
    LiteGraph.registerNodeType("graph/variable", MyVariableNode );
    //LiteGraph.registerNodeType("llm/variable", MyVariableNode );

        //node constructor class
    function MyFileNode()
    {
    this.addOutput("out","string");
    this.addInput("in","string");

    this.addWidget("text","config","", { property: "config"});
    this.addWidget("text","filename","", { property: "filename"});

    this.properties = { filename: "", config:"" };
    }

    //name to show
    MyFileNode.title = "File";

    //register in the system
    LiteGraph.registerNodeType("tools/file", MyFileNode );
    
    
    /*
     * 
     * 
     *   AGENT NODE
     * 
     * 
     */
    //node constructor class
    function MyAgentNode()
    {
    this.addInput("query","string");
    this.addInput("LLM","string");
    this.addInput("tools","string");
    this.addInput("reflexion","string");
    
    this.addOutput("out","string");

    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.properties = {  };
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    }

    //name to show
    MyAgentNode.title = "Agent";
 
    //register in the system
    LiteGraph.registerNodeType("llm/generic_agent", MyAgentNode );


    /*

        INPUT/OUTPUT

    ********************** ******************* */

    //node constructor class
    function MyConnectionNode()
    {
        this.addInput("in","string");
        this.addOutput("out","string");

        this.properties = {conf:"",subtype:"input",template:""  };


        this.addProperty("subtype", "input", "enum", { values: ["input","output"]  });
        this.addWidget("combo","subtype","input",null, { property: "subtype", values: ["input","output"] } );
    }
    //name to show
    MyConnectionNode.title = "Hierarchical connection";
    MyConnectionNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange
    //register in the system
    LiteGraph.registerNodeType("graph/connection", MyConnectionNode );


    /*

        WEB SCRAPER

    */
        //node constructor class
    function MyScraperNode()
    {
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_input","URL",{ property: "address"})
    
    this.properties = { address: "" };
    }

    //name to show
    MyScraperNode.title = "Web scraper";

    //register in the system
    LiteGraph.registerNodeType("tools/web_scraper", MyScraperNode );

    /*

        PDF parser

    */
        //node constructor class
    function MyPDFNode()
    {
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_input","file",{ property: "address"})

    this.properties = { address: "" };
    }

    //name to show
    MyPDFNode.title = "PDF Parser";

    //register in the system
    LiteGraph.registerNodeType("tools/pdf_parser", MyPDFNode );


})(this);
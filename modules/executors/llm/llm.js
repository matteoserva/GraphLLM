


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
/*
    function MyLLMCallNode()
    {
    this.addInput("in","string");

    this.addOutput("out","string");
    this.addOutput("json","string");
    this.gui_node_config = {connection_limits: {max_outputs:2, min_outputs:2}}
    this.properties = {conf:"",subtype:"stateless",template:""  };
    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'


    this.addProperty("subtype", "stateless", "enum", { values: ["stateless","stateful"]  });
    this.addWidget("combo","subtype","stateless",null, { property: "subtype", values: ["stateless","stateful"] } );
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.addCustomWidget( new TitlebarContainer(this));
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.container.addWidget("text_input","Config",{ property: "conf"})
    this.container.addWidget("textarea","template",{ property: "template"})
    }

    //name to show
    MyLLMCallNode.title = "LLM Call";



    MyLLMCallNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange

    //register in the system
    LiteGraph.registerNodeType("llm/llm_call", MyLLMCallNode );

*/







    

    /* ----------------- -------------- */
    //node constructor class
    function MyVirtualSourceNode()
    {
    this.addOutput("out","string");
    this.addInput("sink","virtual",{shape :LiteGraph.ARROW_SHAPE});
    this.addWidget("text","identifier","", { property: "identifier"});

    this.properties = { identifier: "" };
    }

    //name to show
    MyVirtualSourceNode.title = "Virtual Source";

    //function to call when the node is executed
    MyVirtualSourceNode.prototype.onExecute = function(){}

    MyVirtualSourceNode.prototype.onConnectInput = function(target_slot, type, output, source, slot)
    {
        if(source.constructor.name == "MyVirtualSinkNode")
        {
            if(!source.properties.identifier)
            {
                source.setProperty("identifier", LiteGraph.uuidv4())
            }
            this.setProperty("identifier", source.properties.identifier)
        }

        return false;
    }

    //register in the system
    LiteGraph.registerNodeType("graph/virtual_source", MyVirtualSourceNode );

       /* ----------------- -------------- */
    //node constructor class
    function MyVirtualSinkNode()
    {
    this.addInput("in","string");
    this.addWidget("text","identifier","", { property: "identifier"});
    this.addOutput("source","virtual",{shape :LiteGraph.ARROW_SHAPE});
    this.properties = { identifier: "" };
    }

    //name to show
    MyVirtualSinkNode.title = "Virtual sink";

    //function to call when the node is executed
    MyVirtualSinkNode.prototype.onExecute = function(){}

    MyVirtualSinkNode.prototype.onConnectOutput = function(slot, type, input, target_node, target_slot)
    {

        return false;
    }


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

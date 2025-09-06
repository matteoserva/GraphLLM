


(function(global) {

    var LiteGraph = global.LiteGraph;


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




})(this);

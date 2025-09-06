


(function(global) {

    var LiteGraph = global.LiteGraph;


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


})(this);

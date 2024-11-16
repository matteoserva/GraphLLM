
(function(global) {

    var LiteGraph = global.LiteGraph;

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
    LiteGraph.registerNodeType("llm/text_input", MyInputNode );

})(this);
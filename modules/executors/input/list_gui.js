(function(global) {

    var LiteGraph = global.LiteGraph;


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
    LiteGraph.registerNodeType("input/list", MyListNode );

})(this);
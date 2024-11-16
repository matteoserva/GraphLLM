
(function(global) {

    var LiteGraph = global.LiteGraph;

    //node constructor class
    function MyWatchNode()
    {
    this.addInput("in","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_output","",{ property: "parameters"})

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
    function MyCanvasNode()
    {
    this.addInput("in","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("html_canvas","",{ property: "parameters"})

    var tmpl = ""
    this.properties = { };
    }

    //name to show
    MyCanvasNode.title = "HTML Canvas";

    //function to call when the node is executed
    MyCanvasNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    this.container.setValue("parameters",A)
    }

    //register in the system
    LiteGraph.registerNodeType("output/html_canvas", MyCanvasNode );

})(this);



(function(global) {

    var LiteGraph = global.LiteGraph;


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





})(this);

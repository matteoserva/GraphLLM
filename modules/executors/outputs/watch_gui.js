(function(global) {

    var LiteGraph = global.LiteGraph;

    //node constructor class
    function MyWatchNode()
    {
        this.addInput("in","string");

        this.container = new DivContainer(this)
        this.addCustomWidget( this.container);
        this.container.addWidget("text_output","",{ property: "parameters"})

        this.history = ""
        this.properties = { };
    }

    //name to show
    MyWatchNode.title = "Watch";

    //function to call when the node is executed
    /*MyWatchNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    this.container.setValue("parameters",A)
    }*/

    //function to call when the node is executed
    MyWatchNode.prototype.connectPublishers = function(subscribe)
    {
        var source_node = this.getInputNode(0)
        if(source_node)
        {
            var eventId = {type: "print", source: source_node.id.toString()}
            
            subscribe(eventId ,(eventId, eventData) => {this.history += eventData; this.container.setValue("parameters",this.history)} )
            var eventId = {type: "starting", source: source_node.id.toString()}
            subscribe(eventId ,(eventId, eventData) => {this.history = ""})
            var eventId = {type: "output", source: source_node.id.toString(), slot: 0}
            subscribe(eventId ,(eventId, eventData) => {this.container.setValue("parameters",eventData)})
        }
    }


    //register in the system
    LiteGraph.registerNodeType("output/watch", MyWatchNode );

})(this);

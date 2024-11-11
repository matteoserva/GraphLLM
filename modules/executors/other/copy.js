
 (function(global) {

    var LiteGraph = global.LiteGraph;
 /* ********************** ******************* */
    //node constructor class
    function StandardMuxNode()
    {
    this.addInput("in1","string");
	this.addInput("in2","string");

    this.addOutput("out","string");
    this.gui_node_config = {max_outputs:1, min_outputs:1, min_inputs: 2}

    }

    //name to show
    StandardMuxNode.title = "Mux";



    StandardMuxNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange

    //register in the system
    LiteGraph.registerNodeType("graph/standard_mux", StandardMuxNode );

})(this);
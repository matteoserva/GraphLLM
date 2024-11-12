(function(global) {

    var LiteGraph = global.LiteGraph;


        //node constructor class
    function MyWebsocketsNode()
    {
    this.addOutput("receive","string");
    this.addInput("send","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_input","address",{ property: "address"})

    }

    //name to show
    MyWebsocketsNode.title = "Websocket client";

    //register in the system
    LiteGraph.registerNodeType("network/websocket_client", MyWebsocketsNode );
	
})(this);
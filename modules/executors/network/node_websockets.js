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
	
	
	function MyWebsocketsServerNode()
    {
    this.addOutput("receive","string");
    this.addInput("send","string");

	this.properties = { port: 8765 };
	this.addWidget("number","port", 8765, null, { min: 1, max: 65535, step: 10, precision: 0, property: "port" } );
    }

    //name to show
    MyWebsocketsServerNode.title = "Websocket server";

    //register in the system
    LiteGraph.registerNodeType("network/websocket_server", MyWebsocketsServerNode );
	
	
})(this);
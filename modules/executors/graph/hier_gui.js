


(function(global) {

    var LiteGraph = global.LiteGraph;



    /*

        INPUT/OUTPUT

    ********************** ******************* */

    //node constructor class
    function MyConnectionNode()
    {
        this.addInput("in","string");
        this.addOutput("out","string");

        this.properties = {conf:"",subtype:"input",template:""  };


        this.addProperty("subtype", "input", "enum", { values: ["input","output"]  });
        this.addWidget("combo","subtype","input",null, { property: "subtype", values: ["input","output"] } );
    }
    //name to show
    MyConnectionNode.title = "Hierarchical connection";
    MyConnectionNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange
    //register in the system
    LiteGraph.registerNodeType("graph/connection", MyConnectionNode );




})(this);

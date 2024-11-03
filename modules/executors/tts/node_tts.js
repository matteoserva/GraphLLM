(function(global) {

    var LiteGraph = global.LiteGraph;

     /*
     *
     *   TTS
     *
     *
     */

    //node constructor class
    function MyTtsNode()
    {
    this.addInput("in","string");

    this.addProperty("language", "it", "enum", { values: ["it","en"]  });
    this.addWidget("combo","language","it",null, { property: "language", values: ["it_IT-r","en"] } );

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("textarea","",{ property: "parameters"})

    var tmpl = ""
    //this.properties = { };
    }

    //name to show
    MyTtsNode.title = "TTS";

    MyTtsNode.prototype.display = function(val)
    {
        this.container.setValue("parameters",val)

    }

    //register in the system
    LiteGraph.registerNodeType("tools/tts", MyTtsNode );



    //
    //
    //  END TTS
    //

})(this);
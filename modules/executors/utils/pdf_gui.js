


(function(global) {

    var LiteGraph = global.LiteGraph;

    /*

        PDF parser

    */
        //node constructor class
    function MyPDFNode()
    {
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_input","file",{ property: "address"})

    this.properties = { address: "" };
    }

    //name to show
    MyPDFNode.title = "PDF Parser";

    //register in the system
    LiteGraph.registerNodeType("tools/pdf_parser", MyPDFNode );


})(this);




(function(global) {

    var LiteGraph = global.LiteGraph;

    /*

        WEB SCRAPER

    */
        //node constructor class
    function MyScraperNode()
    {
    this.addOutput("out","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addWidget("text_input","URL",{ property: "address"})

    this.properties = { address: "" };
    }

    //name to show
    MyScraperNode.title = "Web scraper";

    //register in the system
    LiteGraph.registerNodeType("tools/web_scraper", MyScraperNode );



})(this);

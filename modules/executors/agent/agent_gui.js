(function(global) {

    var LiteGraph = global.LiteGraph;



   /*
     *
     *
     *   AGENT NODE
     *
     *
     */
    //node constructor class
    function MyAgentNode()
    {
    this.addInput("query","string");


    this.addOutput("out","string");
    this.addOutput("LLM","string");
    this.addOutput("tools","string");
    this.addOutput("reflexion","string");

    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    //this.container.addElement(new CustomTextarea("Parameters","parameters"))

    this.properties = {  };
    this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    }

    //name to show
    MyAgentNode.title = "Agent";

    //register in the system
    LiteGraph.registerNodeType("llm/generic_agent", MyAgentNode );

})(this);

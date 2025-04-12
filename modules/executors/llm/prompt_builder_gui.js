
 (function(global) {

    var LiteGraph = global.LiteGraph;
 /* ********************** ******************* */
    //node constructor class
    function PromptBuilderNode()
    {
    this.addInput("in","string");

    this.addOutput("simple","string");
    this.addOutput("GraphLLM","string");
    this.gui_node_config = {connection_limits: {max_outputs:3, min_outputs:3}}
    this.properties = {conf:"",subtype:"stateless",template:""  };
    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);

    this.container.addWidget("textarea","template",{ property: "template"})
    }

    //name to show
    PromptBuilderNode.title = "Prompt builder";



    PromptBuilderNode.prototype.onConnectionsChange = MyGraphNode.prototype.onConnectionsChange

    //register in the system
    LiteGraph.registerNodeType("llm/prompt_builder", PromptBuilderNode );

})(this);
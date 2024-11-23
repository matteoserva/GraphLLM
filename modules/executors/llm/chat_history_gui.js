(function(global) {

    var LiteGraph = global.LiteGraph;

    function chat_history_onstart()
    {
        this.saved_history = JSON.parse(JSON.stringify(this.properties["parameters"]))
        if((this.saved_history.length % 2) != 1)
        {
            this.saved_history.push("")
        }
    }

    function chat_history_onexecute()
    {
        var A = this.getInputData(0);
        if( A !== undefined )
        {
            var new_history = JSON.parse(JSON.stringify(this.saved_history))
            var message_index = new_history.length-1
            new_history[message_index] =this.saved_history[message_index] + A
            this.container.setValue("parameters",new_history)
        }
    }

        /****
     *
     *
     *
     * chat history NODE
     *
     * */
    function MyChatHistoryNode()
    {
    this.addOutput("out","string");
    //this.addInput("in","string");

    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    var listWidget = this.container.addWidget("list","Parameters",{ property: "parameters", cell_name_generator: "prompt"})

    //this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = {  };
    }

    //name to show
    MyChatHistoryNode.title = "Chat History";

    //register in the system
    LiteGraph.registerNodeType("llm/chat_history", MyChatHistoryNode );

    MyChatHistoryNode.prototype.connectPublishers = function(subscribe) {
            // output
            var source_location = {position: "output", slot: 0, filter: "llm_call"}
            var eventId = {type: "output", slot: 0};
            var action = {type: "container_action", target: "set", parameter: "parameters"}
            subscribe(this, source_location, eventId, action)

            // output
            var source_location = {position: "output", slot: 0, filter: "llm_call"}
            var eventId = {type: "print"};
            var action = {type: "container_action", target: "append", parameter: "parameters"}
            subscribe(this, source_location, eventId, action)
    }

    MyChatHistoryNode.prototype.onStart = chat_history_onstart;

    MyChatHistoryNode.prototype.onExecute = chat_history_onexecute;

})(this);
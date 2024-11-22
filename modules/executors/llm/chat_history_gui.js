(function(global) {

    var LiteGraph = global.LiteGraph;

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
    var listWidget = this.container.addWidget("list","Parameters",{ property: "parameters"})
    listWidget.makeCellName = function(index)
    {
        if(index == 0)
        {
                return "system";
        }
        else if(index % 2)
        {
                return "user";
        }
        else
        {
                return "assistant"
        }
        return index+1
    }
    listWidget.reset()
    //this.container.addWidget("textarea","Parameters",{ property: "parameters"})
    this.properties = {  };
    }

    //name to show
    MyChatHistoryNode.title = "Chat History";

    //register in the system
    LiteGraph.registerNodeType("llm/chat_history", MyChatHistoryNode );

    MyChatHistoryNode.prototype.onStart = function()
    {
        this.saved_history = JSON.parse(JSON.stringify(this.properties["parameters"]))
        if((this.saved_history.length % 2) != 1)
        {
            this.saved_history.push("")
        }
    }

    MyChatHistoryNode.prototype.onExecute = function()
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

})(this);
(function(global) {

        var LiteGraph = global.LiteGraph;
        /* ********************** *******************
                WatchNodeGui: Watch
         ********************** *******************  */
        //node constructor class
/*
        function WatchNodeGui()
        {
            this.addInput("in","string");
            this.container = new DivContainer(this)
            this.addCustomWidget( this.container);
            this.container.addWidget('text_output', '', {'property': 'parameters'})
            this.history = {};


        }

        WatchNodeGui.prototype.connectPublishers = function(subscribe) {
            // output
            var source_location = {position: "input", slot: 0}
            var eventId = {type: "output", slot: 0};
            var action = {type: "container_action", target: "set", parameter: "parameters"}
            subscribe(this, source_location, eventId, action)

            // print
            var source_location = {position: "input", slot: 0}
            var eventId = {type: "print"};
            var action = {type: "container_action", target: "append", parameter: "parameters", silent: true}
            subscribe(this, source_location, eventId, action)

            // starting -> reset
            var source_location = {position: "input", slot: 0}
            var eventId = {type: "starting"};
            var action = {type: "container_action", target: "reset", parameter: "parameters"}
            subscribe(this, source_location, eventId, action)

        }


        WatchNodeGui.title = "Watch"
        //LiteGraph.registerNodeType("outpute/watch", WatchNodeGui );
*/

        })(this);


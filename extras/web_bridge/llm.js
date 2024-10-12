


(function(global) {




    var LiteGraph = global.LiteGraph;


    //node constructor class
    function MyGraphNode()
    {
    this.addInput("in","string");
    
    this.addOutput("out","string");

    let tmpl = 'type: python\ninit: "test/python_hello_world.py"'
    
    //this.addWidget("text","Parameters", tmpl, function(v){}, { multiline:true, property:"parameters" } );
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addElement(new CustomTextarea("Parameters","parameters"))
    //this.container.addElement(new CustomTextarea())
    
    this.properties = { parameters: tmpl };
    this.setSize( this.computeSize() );
    }

    //name to show
    MyGraphNode.title = "Graph";

    //function to call when the node is executed
    MyGraphNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    if( A === undefined )
        A = 0;
    var B = this.getInputData(1);
    if( B === undefined )
        B = 0;
        //let xhr = new XMLHttpRequest();
        //xhr.open('GET', '/graph/exec',false);
        //xhr.send();
        //console.log(xhr.response);
    //this.setOutputData( 0, xhr.response );
    
    //
    }
    
    MyGraphNode.prototype.onStart = function()
    {
        console.log("started")
   
    }
    
    MyGraphNode.prototype.onRemoved = function()
    {
        console.log("started")
        this.container.remove()
   
    }
 
    MyGraphNode.prototype.onPropertyChanged= function( k, val )
    {
        var numArgs = arguments.length
        if(numArgs == 2)
        this.container.setValue(k,val)
        
    }

    MyGraphNode.prototype.onConnectionsChange = function(dir,slot,connected,d,e)
    {
        console.log("dir: " +dir + "  slot: " + slot + "  connected: "  + connected )
        if(dir == LiteGraph.INPUT)
        {
              if(connected)
              {
                  let numInputs = this.inputs.length
                  if(slot +1 == numInputs && !!d)
                  {
                    this.addInput("N","string"); 
                    //this.setSize( this.computeSize() );
                  }
              
              }
              else
              {
                    let numInputs = this.inputs.length
                    let maxInput = 0;
                    for (let i = 1; i < numInputs; i++) {
                        if(!!this.inputs[i].link)
                        {
                            maxInput = i
                        }
                    }
                     for (let i = numInputs-1; i > maxInput+1; i--) {
                      
                            this.removeInput(i)
                            //this.setSize( this.computeSize() );
                     
                    }
                }
        }
    }
    
    //register in the system
    LiteGraph.registerNodeType("llm/graph", MyGraphNode );
    
    //node constructor class
    function MyWatchNode()
    {
    this.addInput("in","string");
    
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addElement(new CustomTextarea("Parameters","parameters"))
    
    var tmpl = ""
    this.properties = { parameters: tmpl };
    this.setSize( this.computeSize() );
    }

    //name to show
    MyWatchNode.title = "Watch";

    //function to call when the node is executed
    MyWatchNode.prototype.onExecute = function()
    {
    var A = this.getInputData(0);
    this.container.setValue("parameters",A)
    }
    
    //register in the system
    LiteGraph.registerNodeType("llm/watch", MyWatchNode );
    
    //node constructor class
    function MyInputNode()
    {
    this.addOutput("out","string");
    
    this.container = new DivContainer(this)
    this.addCustomWidget( this.container);
    this.container.addElement(new CustomTextarea("Parameters","parameters"))
    
    var tmpl = ""
    this.properties = { parameters: tmpl };
    this.setSize( this.computeSize() );
    }

    //name to show
    MyInputNode.title = "Input";

    //function to call when the node is executed
    MyInputNode.prototype.onExecute = function()
    {
    
    
    }
    
    //register in the system
    LiteGraph.registerNodeType("llm/input", MyInputNode );
    
})(this);

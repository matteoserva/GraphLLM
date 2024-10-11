
class CustomTextarea {
        constructor(name,property)
        {
                this.disabled = false
                this.name=name
                this.value=""
                this.H = 15
                this.type = "custom"
                this.options = {multiline:true}
                this.y=0
                this.div = this.makeElement()
                
                this.inFocus = false
                this.margin = 5
                this.property = property
                this.connected = false
        }

        
        
        makeElement(node,canvas, parentElement)
        {         
                var dialog = parentElement
                var div = document.createElement("div");
                var text = document.createElement("div");
                text.innerText = this.name
                text.style="position:absolute; top:2px; right:4px; color:DarkGray; user-select: none"
                div.appendChild(text)
                div.style="position:relative";
                var textarea = document.createElement("textarea");
                div.appendChild(textarea)
                textarea.class="value"
                textarea.style='resize:none;white-space: nowrap;margin-bottom:' + this.margin + 'px'
                textarea.style.backgroundColor= "black" 
                textarea.style.color = "white"
                textarea.style.width = "100%";
                

                
                this.textarea = textarea
                return div
            
        }
        appendElement(node,canvas, parentElement)
        {         
                var dialog = parentElement
                dialog.appendChild(this.div);
                var textarea = this.textarea
                textarea.addEventListener("focusout", function(event){console.log("focusout"), this.inFocus = false}.bind(this))
                textarea.addEventListener("focusin", function(event){this.textareaFocus(node,textarea)}.bind(this))
                textarea.addEventListener("keyup", function(event){this.textChange(node)}.bind(this))
                this.connected = true
            
        }
        
        textChange(node)
        {
               var value = this.textarea.value
               if(this.property)
               {
                node.setProperty(this.property,value)
               }
        }
        
        configureSize(aSpace)
        {
            var availableSpace = aSpace - this.margin
            var textarea = this.textarea
            textarea.style.height = "1px";
            var scrollHeight = textarea.scrollHeight;
            var desiredHeight = 30
            
            var minSize = 30;
            if (this.inFocus)
            {
                desiredHeight = (15+ textarea.scrollHeight)
            }
            desiredHeight = Math.max(availableSpace,desiredHeight,minSize)
            textarea.style.height = desiredHeight + "px"
            this.H = desiredHeight;//this.dialog.clientHeight
            //console.log(desiredHeight)
            
        }
        
        
        textareaFocus(node,textarea)
        {
            console.log("focusin");
            this.inFocus = true
            this.configureSize(this.H+this.margin)
            //node.setProperty("parameters","ciao")
            //textarea.style.height = "1px";
            //var scrollHeight = textarea.scrollHeight;
            //textarea.style.height = (15+ textarea.scrollHeight)+"px";
        }
        
        updateTextarea(node,canvas,y,H)
        {

            var scale = canvas.ds.scale
            var posX = node.pos[0] + 15 + canvas.ds.offset[0]
            var posY = node.pos[1] + this.y + canvas.ds.offset[1]
            posX *= scale 
            posY *= scale 
                this.dialog.style.left = posX + "px";
            this.dialog.style.top = posY + "px";
            this.dialog.style.width = (node.size[0]-30) + "px";
            this.dialog.style.transform = "scale(" + canvas.ds.scale + ")"
            this.dialog.style.transformOrigin = "top left"
            var textarea = this.dialog.querySelector("textarea")
            this.configureSize(node,textarea)
        }
        

        computeSize(widget_width)
        {
           var res = [widget_width, this.H]
           return res
        }

        draw(ctx, node, widget_width, y, H)
        {
            
            this.configureSize(H)
            
        }
        setValue(k,v)
        {
            this.textarea.value=v
        }

}

class DivContainer {
        constructor(parent)
        {
                this.disabled = false
                this.name="Parameters"
                this.value=""
                
                this.type = "custom"
                this.saved_y=0
                this.height = 50
                this.H = 50
                this.children = []
                this.options = {}
        }

        makeTextarea(node)
        {
                var canvas = node.graph.list_of_graphcanvas[0]           
                var dialog = document.createElement("div");
                dialog.style.position = "absolute";
                dialog.innerHTML = "";
                
                dialog.style.height = this.height + "px";
                dialog.style.backgroundColor= "black" 
                canvas.canvas.parentNode.appendChild(dialog);
                this.dialog = dialog
                this.children.forEach(function(v,i,a){v.appendElement(node,canvas,dialog)})
            
        }
        
        configureSize(node,textarea,H)
        {
            var y = this.saved_y
            this.H = this.height ;//this.dialog.clientHeight
        }
        
        
        updateTextarea(node,canvas,y,H)
        {
            this.dialog.style.width = (node.size[0]-30) + "px";
            var scale = canvas.ds.scale
            var posX = node.pos[0] + 15 + canvas.ds.offset[0]
            var posY = node.pos[1] + this.saved_y + canvas.ds.offset[1]
            posX *= scale 
            posY *= scale 
            this.dialog.style.left = posX + "px";
            this.dialog.style.top = posY + "px";
            this.dialog.style.width = (node.size[0]-30) + "px";
            this.dialog.style.transform = "scale(" + canvas.ds.scale + ")"
            this.dialog.style.transformOrigin = "top left"
            var textarea = this.dialog.querySelector("textarea")
            this.configureSize(node,textarea,H)
            var numChildren = this.children.length
            this.H = numChildren * this.height
            
        }
        

        computeSize(widget_width)
        {
           var res = [widget_width, this.H]
           return res
        }

        draw(ctx, node, widget_width, y, H)
        {
            //this.H = 2*H
            this.saved_y = y;
            
            if (!this.dialog)
            {
                //var canvas = node.graph.list_of_graphcanvas[0]
                this.makeTextarea(node)
                
            }
            this.updateTextarea(node,node.graph.list_of_graphcanvas[0],y,this.H)
            var availableSpace = node.size[1] - y
            var numChildren = this.children.length
            var childrenSpace = (availableSpace-5)/numChildren
            this.children.forEach(function(v,i,a){v.draw(ctx, node, widget_width, y, childrenSpace)})
        }
        
        addElement(element)
        {
            this.children.push(element)
            
        }
        setValue(k,val)
        {
            this.children.forEach(function(v,i,a){v.setValue(k,val)})
        }
        remove()
        {
            this.dialog.parentNode.removeChild(this.dialog)
        }
}

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
})(this);

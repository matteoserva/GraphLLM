class CustomTextarea {
    constructor(parent,name,options)
    {
        this.disabled = false
        this.name=name
        this.value=""
        this.H = 15
        this.type = "custom"
        this.options = {multiline:true}
        this.y=0
        this.div = this.makeElement(parent)
        
        this.inFocus = false
        this.margin = 5
        this.property = options.property
        this.parent = parent
        
    }
    
    
    
    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        var text = document.createElement("div")
        text.className = "nameText";
        text.innerText = this.name
        text.style="position:absolute; top:2px; right:4px; color:DarkGray; user-select: none"
        div.appendChild(text)
        div.style="position:relative";
        div.style.height = "100%";
        var textarea = document.createElement("textarea");
        div.appendChild(textarea)
        textarea.className="CustomTextarea"
        textarea.style='resize:none; white-space: pre;border:0px;padding:0px' + this.margin + 'px'
        textarea.style.backgroundColor= "black" 
        textarea.style.color = "white"
        textarea.style.width = "100%";
        textarea.style.height = "100%";
        this.textarea = textarea
        
        textarea.addEventListener("focusout", function(event){this.textareaUnfocus(textarea)}.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div
        
    }
    
    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }
    
    detachElement()
    {
        this.div.remove()
    }
    
    textChange()
    {
        var value = this.textarea.value
        if(this.property)
        {
            this.parent.notifyValue(this,this.property,value)
        }
        this.configureSizeInFocus()
    }
    
    configureSizeInFocus()
    {
        var textarea = this.textarea
        if (this.inFocus)
        {
            
        
        this.textarea.style.whiteSpace="pre"
            textarea.style.width = "1px";
            textarea.style.height = "1px";
            textarea.style.minHeight = ""
            textarea.style.minWidth = ""
            
            var minHeight = (textarea.scrollHeight);
            var minWidth = (textarea.scrollWidth);
            textarea.style.width = "100%";
            textarea.style.height = "100%";
            var currentWidth = textarea.clientWidth
            var currentHeight = textarea.clientHeight
            
            minWidth = Math.min(minWidth,window.innerWidth*0.7)
            minHeight = Math.min(minHeight,window.innerHeight*0.7)
            textarea.style.minHeight = (minHeight+10) + "px"
            textarea.style.minWidth = (minWidth+15)  + "px"
            this.textarea.style.whiteSpace="pre-wrap"
        }
        
    }
    
    configureSize(aSpace,hSpace)
    {
        var textarea = this.textarea

        if (this.inFocus)
        {
        }
        else
        {
            textarea.style.width = "100%";
            textarea.style.height = "100%";
            textarea.style.minHeight = ""
            textarea.style.minWidth = ""
        }
        
    }
    
    
    textareaFocus(textarea)
    {
        console.log("focusin");
        this.inFocus = true
        this.configureSize(this.H+this.margin)
        this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="none"
        var container = this.div.closest(".div-container")
        container.style.zIndex = 1
        this.div.style.zIndex = 1
        this.configureSizeInFocus()
    }
    
    textareaUnfocus(textarea)
    {
        console.log("focusout")
        this.inFocus = false
        this.configureSize()
        this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="block"
        var container = this.div.closest(".div-container")
        container.style.zIndex = ""
        this.div.style.zIndex = ""
        this.textarea.style.whiteSpace="pre"
        this.textChange()
    }
    
    computeSize(widget_width)
    {
        var res = [widget_width, this.H]
        return res
    }
    
    draw(ctx, node, widget_width, y, H)
    {
        this.configureSize(H,widget_width)
        
    }
    setValue(k,v)
    {
        if(this.textarea.value!=v)
        {
        this.textarea.value=v
        this.configureSizeInFocus()
        }
    }
    getMinHeight()
    {
        return 50;
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
        this.parent = parent
        this.attached = false
        this.parent.onRemoved = function(){this.remove()}.bind(this)
        var that = this
        this.parent.onPropertyChanged= function( k, val )
        {
            var numArgs = arguments.length
            if(numArgs == 2)
                that.setValue(k,val)
                
        }
        var oldCollapse = this.parent.collapse.bind(this.parent)
        this.parent.collapse = function()
        {
            oldCollapse()
            this.onCollapse()
        }.bind(this)
        
        
        setTimeout(function(){
            let newSize = this.parent.computeSize();
            newSize[0] = Math.max(newSize[0],this.parent.size[0])
            newSize[1] = Math.max(newSize[1],this.parent.size[1])
            this.parent.setSize( newSize)
        }.bind(this) );
        
        this.makeElement()
        
        this.drawCounter = 0;
        this.parent.onBounding = function(out)
        {
            if(this.drawCounter == 0)
            {
                
                if(this.dialog){this.dialog.style.display="none"}
            }
            this.drawCounter = 0;
        }.bind(this)
        
    }
    
    onCollapse()
    {
        var collapsed = this.parent.flags.collapsed
        if(collapsed)
        {
            this.dialog.style.display ="none"
        }
        else
        {
            this.dialog.style.display =""
            
        }
        
    }
    
    makeElement()
    {
                
        var dialog = document.createElement("div");
        dialog.className = "div-container";
        dialog.style.position = "absolute";
        dialog.innerHTML = "";
        
        dialog.style.height = this.height + "px";
        //dialog.style.backgroundColor= "black" 
        
        this.dialog = dialog

    }
    
    appendElement(node)
    {
        var canvas = node.graph.list_of_graphcanvas[0]
        var dialog = this.dialog
        canvas.canvas.parentNode.appendChild(dialog);
        this.attached = true
    }
    
    configureSize(node,textarea,H)
    {
        var y = this.saved_y
        this.H = this.height ;//this.dialog.clientHeight
    }
    
    
    updateTextarea(node,canvas,y,availableSpace)
    {
        //this.dialog.style.width = (node.size[0]-30) + "px";
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
        this.dialog.style.height = (availableSpace-10) + "px"
        this.dialog.style.display = "inline-block"
        var textarea = this.dialog.querySelector("textarea")
        this.configureSize(node,textarea,availableSpace)
        var numChildren = this.children.length
        this.H = numChildren * this.height
        this.drawCounter = 1;
        
    }
    
    
    computeSize(widget_width)
    {
        var minHeight = 0;
        for(let i = 0; i < this.children.length; i++)
        {
            var childMinHeight = 0
            if(this.children[i].getMinHeight)
            {
                    childMinHeight = this.children[i].getMinHeight()
            }
            minHeight += childMinHeight;
        }
        if(minHeight<50)
        {
                minHeight = 50;
        }
        var res = [widget_width, minHeight]
        return res
    }
    
    draw(ctx, node, widget_width, y, H)
    {
        //this.H = 2*H
        this.saved_y = y;
        
        if (!this.attached)
        {
            //var canvas = node.graph.list_of_graphcanvas[0]
            this.appendElement(node)
            
        }
        
        var availableSpace = node.size[1] - y
        this.updateTextarea(node,node.graph.list_of_graphcanvas[0],y,availableSpace)
        var numChildren = this.children.length
        var childrenSpace = (availableSpace-5)
        for(let i = 0; i < numChildren; i++)
        {
            var child = this.children[i]
            var remainingChildren = numChildren-i
            var childSpace = childrenSpace/remainingChildren
            child.draw(ctx, node, widget_width, y, childSpace)
        }
        
        
        // not neede this.drawCounter=1;
        this.dialog.style.display="flex"
        this.dialog.style.flexDirection="column"
        var mySize = this.computeSize()
        if(mySize[1] > availableSpace)
        {
                var saved_x = this.parent.size[0]
                this.parent.setSize(this.parent.computeSize())
            this.parent.size[0] = saved_x
            this.parent.setDirtyCanvas(true, true);
        }
    }
    
    addElement(element)
    {
        this.children.push(element)
        element.appendElement(this.dialog)
        
    }
    addWidget(type, name, options)
    {
        if(type == "list")
        {
            var elem = new CustomList(this, name,options)
            this.addElement(elem)
        }
        else
        {
            var elem = new CustomTextarea(this, name,options)
            this.addElement(elem)
        }
        return elem
    }
    
    notifyValue(me, k,val)
    {
        this.parent.setProperty(k,val)
    }
    
    setValue(k,val)
    {
        this.children.forEach(function(v,i,a){v.setValue(k,val)})
    }
    
    remove()
    {
        if(this.dialog)
        {
            this.dialog.remove()
        }
    }
}

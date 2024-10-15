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
                this.div = this.makeElement()
                
                this.inFocus = false
                this.margin = 5
                this.property = options.property
                this.connected = false
                this.parent = parent

        }

        
        
        makeElement(node,canvas, parentElement)
        {
                var dialog = parentElement
                var div = document.createElement("div");
                var text = document.createElement("div")
                text.className = "nameText";
                text.innerText = this.name
                text.style="position:absolute; top:2px; right:4px; color:DarkGray; user-select: none"
                div.appendChild(text)
                div.style="position:relative";
                var textarea = document.createElement("textarea");
                div.appendChild(textarea)
                textarea.className="CustomTextarea"
                textarea.style='resize:none; white-space: pre;border:0px;padding:0px' + this.margin + 'px'
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
                textarea.addEventListener("focusout", function(event){this.textareaUnfocus(node,textarea)}.bind(this))
                textarea.addEventListener("focusin", function(event){this.textareaFocus(node,textarea)}.bind(this))
                textarea.addEventListener("keyup", function(event){this.textChange(node)}.bind(this))
                this.connected = true
            
        }
        
        textChange(node)
        {
               var value = this.textarea.value
               if(this.property)
               {
                    this.parent.notifyValue(this.property,value)
               }
        }
        
        configureSize(aSpace,hSpace)
        {
            var availableSpace = aSpace - this.margin
            var textarea = this.textarea
            textarea.style.height = "1px";
            var scrollHeight = textarea.scrollHeight;
            var scrollWidth = textarea.scrollWidth;
            var currentWidth = textarea.clientWidth
            var desiredHeight = 30
            
            var minSize = 30;
            var desiredWidth = "100%"
            if (this.inFocus)
            {
                desiredHeight = (15+ textarea.scrollHeight)
                textarea.style.width = "1px";
                if((textarea.scrollWidth+10) > textarea.parentNode.clientWidth)
		{
                	desiredWidth = (10+ textarea.scrollWidth)+ "px"
		}
            }
            desiredHeight = Math.max(availableSpace,desiredHeight,minSize)
            //this.dialog.style.width = desiredWidth
            textarea.style.width = desiredWidth
            textarea.style.height = desiredHeight + "px"
            this.H = desiredHeight;//this.dialog.clientHeight
            //console.log(desiredHeight)
            
        }
        
        
        textareaFocus(node,textarea)
        {
            console.log("focusin");
            this.inFocus = true
            this.configureSize(this.H+this.margin)
	    this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="none"
        }

	textareaUnfocus(node,textarea)
	{
		console.log("focusout")
		this.inFocus = false
		this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="block"
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
                this.parent = parent
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
		//console.log(this.parent.flags.collapsed)
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
        addWidget(type, name, options)
        {
            var elem = new CustomTextarea(this, name,options)
            this.addElement(elem)
        }

        notifyValue(k,val)
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
           // this.dialog.parentNode.removeChild(this.dialog)
        }
}

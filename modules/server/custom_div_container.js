
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

        this.saved_values = {}
        this.saved_diff = {}
		
		
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

        var innerDialog = document.createElement("div");
        innerDialog.className = "div-innercontainer";

        this.innerDialog = innerDialog
        dialog.appendChild(innerDialog)
        this.dialog = dialog


        var titlebar = document.createElement("div");
        titlebar.className = "titlebar-container";
        titlebar.style.position = "absolute";
        titlebar.innerHTML = " ";
        this.titlebar = titlebar
        dialog.appendChild(titlebar)
		
		setTimeout(function(){
            if(this.parent.id)
			{
				this.appendElement(this.parent)
			}
        }.bind(this) );
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
        this.dialog.style.height = (availableSpace-15) + "px"
        this.dialog.style.display = "inline-block"
        var textarea = this.dialog.querySelector("textarea")
        this.configureSize(node,textarea,availableSpace)
        var numChildren = this.children.length
        this.H = numChildren * this.height
        this.drawCounter = 1;

        this.titlebar.style.top = (-this.saved_y - 20) + "px";
        this.titlebar.style.right = "0px";

    }


    computeSize(widget_width)
    {

        this.innerDialog.style.height = "min-content"
        var scrollHeight = this.innerDialog.clientHeight
        this.innerDialog.style.height = "100%"

        return [undefined,scrollHeight]
    }

    draw(ctx, node, widget_width, y, H)
    {
        //this.H = 2*H
        this.saved_y = y;

        var availableSpace = node.size[1] - y
        this.updateTextarea(node,node.graph.list_of_graphcanvas[0],y,availableSpace)
        var numChildren = this.children.length
        var childrenSpace = (availableSpace-5)
        for(let i = 0; i < numChildren; i++)
        {
            var child = this.children[i]
            var remainingChildren = numChildren-i
            var childSpace = childrenSpace/remainingChildren
            if(child.draw)
            {
                child.draw(ctx, node, widget_width, y, childSpace)
             }
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
        element.appendElement(this.innerDialog )

    }
    addWidget(type, name, options)
    {
        if(type == "list")
        {
            var elem = new CustomList(this, name,options)
            this.addElement(elem)
        }
        else if(type=="text_input")
        {
            var elem = new CustomTextInput(this, name,options)
            this.addElement(elem)
        }
        else if(type=="text_output")
        {
            var elem = new CustomTextOutput(this, name,options)
            this.addElement(elem)
        }
        else if(type=="html_canvas")
        {
            var elem = new CustomHtmlCanvas(this, name,options)
            this.addElement(elem)
        }
        else if(type=="file_drop")
        {
            var elem = new CustomFileDrop(this, name,options)
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
        this.parent.setDirtyCanvas(true, true);
        this.saved_values[k] = JSON.parse(JSON.stringify(val))
        this.saved_diff[k] = ""
    }

    setValue(k,val,save=true)
    {

        if(save)
        {
            this.saved_values[k] = JSON.parse(JSON.stringify(val))
            this.saved_diff[k] = ""
        }
        this.children.forEach(function(v,i,a){v.setValue(k,val)})
    }

    executeAction(eventId, action, data)
    {
        if(action.type == "widget_action")
        {
            var filtered = this.children.filter((el) => el.property== action.property)
            var child = filtered[0]
            if(child)
            {
                child.executeAction(eventId, action, data)
            }

        }
        else if(action.target == "set")
        {
            if(Array.isArray(this.saved_values[action.parameter]))
            {
                var user_value = this.saved_values[action.parameter]
                var message_index = user_value.length-1
                user_value[message_index] += data
                var newValue = user_value
            }
            else
            {
                this.saved_diff[action.parameter] = data
                var newValue = this.saved_values[action.parameter] + this.saved_diff[action.parameter]

            }
            this.setValue(action.parameter,newValue)
            if(!action.silent)
            {
                this.notifyValue(this,action.parameter,newValue)
            }
        }
        else if(action.target == "append")
        {
            this.saved_diff[action.parameter] += data
            if(Array.isArray(this.saved_values[action.parameter]))
            {
                var newValue = [...this.saved_values[action.parameter]];
                var message_index = newValue.length-1
                newValue[message_index] = newValue[message_index] +this.saved_diff[action.parameter]
            }
            else
            {
                var newValue = this.saved_values[action.parameter] + this.saved_diff[action.parameter]
            }
            this.setValue(action.parameter,newValue,false)
        }
        else if(action.target == "reset")
        {
            this.saved_values[action.parameter] = ""
            this.saved_diff[action.parameter] = ""
        }
    }

    remove()
    {
        if(this.dialog)
        {
            this.dialog.remove()
        }
    }
}
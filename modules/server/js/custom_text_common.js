
class CustomTextCommon{
    constructor(parent,name,options)
        {
            this.disabled = false
            this.name=name
            this.value=""
            this.H = 15
            this.type = "custom"
            this.y=0
            this.div = this.makeElement(parent)
            this.div.classList.add('deselected');
            this.inFocus = false
            this.margin = 5
            this.property = options.property
            this.parent = parent
            if ("default" in options)
            {
                this.textarea.value=options.default
                this.parent.notifyValue(this,this.property,options.default)
            }
            this.format = options.format
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
        if(this.property && (typeof value !== 'undefined'))
        {
            if(this.format == "json")
            {
                try {
                    value = JSON.parse(value)
                } catch (error) {}
            }
            this.parent.notifyValue(this,this.property,value)
        }
        this.configureSizeInFocus()
    }

    textareaFocus(textarea)
    {
        console.log("focusin");
        var previousHeight =  this.div.clientHeight
        this.div.classList.remove('deselected');
        this.div.classList.add('selected');

        this.inFocus = true
        this.configureSize(this.H+this.margin)
        //this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="none"
        var container = this.div.closest(".div-container")
        container.style.zIndex = 1
        this.div.style.zIndex = 1
        this.div.style.flexGrow = null

        this.configureSizeInFocus()
        this.div.style.height = "" + previousHeight + "px"
    }

    textareaUnfocus(textarea)
    {
        console.log("focusout")
        var scrollTop = this.textarea.scrollTop //BUG WORKAROUND:save the scroll before playing with size
        var totally_scrolled = this.textarea.scrollTop >= 5 &&
            (Math.abs(this.textarea.scrollHeight - this.textarea.clientHeight - this.textarea.scrollTop) <= 1);

        this.div.classList.remove('selected');
        this.div.classList.add('deselected');
        this.inFocus = false
        this.configureSize()
        //this.textarea.parentNode.getElementsByClassName("nameText")[0].style.display="block"
        var container = this.div.closest(".div-container")
        container.style.zIndex = ""
        this.div.style.zIndex = ""
        this.div.style.height = null
        this.textarea.style.whiteSpace="pre"
        this.textChange()

        if(totally_scrolled)
        {
            this.textarea.scrollTo(0,this.textarea.scrollHeight)
        }
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
        if(this.format == "json")
        {
            v = JSON.stringify(v)
        }
        if(this.property && this.property == k && this.textarea.value!=v)
        {
            var scrollTop = this.textarea.scrollTop //BUG WORKAROUND:save the scroll before playing with size
            var totally_scrolled = this.textarea.scrollTop >= 0 &&
                (Math.abs(this.textarea.scrollHeight - this.textarea.clientHeight - this.textarea.scrollTop) <= 1);

            if(this.textarea.tagName.toLowerCase() == "div")
            {
                this.setDisplayValue(v)
            }
            else
            {
                this.textarea.value=v
            }
            this.configureSizeInFocus()
            if(totally_scrolled)
            {
                this.textarea.scrollTo(0,this.textarea.scrollHeight)
            }
            else
            {
                this.textarea.scrollTop = scrollTop
            }
        }
    }
    getMinHeight()
    {
        return this.minHeight;
    }
	
	handleFocusOutEvent(event,textarea)
	{
			if (event.relatedTarget === null) {
				setTimeout(function () { event.target.focus()},0);
				console.log("focus null bloccato")
				return;
			}
			if (event.relatedTarget.tagName.toUpperCase() == "CANVAS") {
				setTimeout(handleCanvasFocus.bind(this,event),0);
				
				/*LiteGraph.pointerListenerAdd(event.relatedTarget,"up", function(){
					console.log("canvas nup");
					
					
				},{once: true, capture:true});*/
				console.log("focus canvas bloccato")
				return;
			}
			
			this.textareaUnfocus(textarea)
		
		
			function handleCanvasFocus(event)
			{
				var is_dragging = event.relatedTarget.data.pointer_is_down &&  event.relatedTarget.data.dragging_canvas
				if(is_dragging)
				{
					var canvas = event.relatedTarget.data
					var last_click_position = canvas.last_click_position
					LiteGraph.pointerListenerAdd(event.relatedTarget.data.getCanvasWindow().document,"up", function(){
						console.log("canvas document up");
						
						if(last_click_position[0] == canvas.mouse[0] || 
							last_click_position[1] == canvas.mouse[1] ||
                                                        (!event.target.checkVisibility())      )
						{
							console.log ("canvas up mouse not moved")
							event.relatedTarget.focus()
							this.textareaUnfocus(textarea)
						}
						else
						{
							event.target.focus({ preventScroll: true })
							
						}
						
					}.bind(this),{once: true, capture:true});
				}
				else
				{
					event.relatedTarget.focus()
					this.textareaUnfocus(textarea)
				}
			}
		
	}

}

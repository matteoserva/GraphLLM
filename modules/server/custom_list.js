class CustomList {
    constructor(parent,name,options)
    {
        this.children = []
        this.disabled = false
        this.name=name
        this.value=[]
        this.H = 15
        this.type = "custom"
        this.options = {multiline:true}
        this.y=0
        this.div = this.makeElement(parent)
        
        this.inFocus = false
        this.margin = 5
        this.property = options.property
        this.parent = parent
        this.height = 100
        
        
    }
    
    
    
    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.style = "display:flex;flex-direction:column;"
        var buttonDiv = document.createElement("div");
        buttonDiv.style = "display:flex;"
        var minus = document.createElement("button");
        minus.innerText="-"
        buttonDiv.appendChild(minus)
        var plus = document.createElement("button");
        plus.innerText="+"
        plus.style="margin-left: auto; margin-right: 0;"
        buttonDiv.appendChild(plus)
        div.appendChild(buttonDiv)
        
        plus.addEventListener("click", this.addTextBox.bind(this))
        minus.addEventListener("click", this.removeTextBox.bind(this))
        this.div = div
        this.addTextBox()
        this.addTextBox()
        return div
    }
    
    addTextBox()
    {
        var index = this.children.length
        var element = new CustomTextarea(this, index,{property:"ciao"})
        element.appendElement(this.div)
        this.children.push(element)
        this.value.push("")
    }
    
    removeTextBox()
    {
        if(this.children.length > 2)
        {
            var child = this.children.pop()
            child.detachElement()
            while(this.value.length > this.children.length)
            {
                    this.value.pop()
            }
            this.parent.notifyValue(this, this.property,this.value)
            
        }
    }
    
    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }
    
    notifyValue(me, k,val)
    {
        var index =this.children.indexOf(me)
        console.log(index,k,val)
        this.value[index] = val
        this.parent.notifyValue(me, this.property,this.value)
    }
    
    textChange()
    {
        var value = this.textarea.value
        if(this.property)
        {
            this.parent.notifyValue(this.property,value)
        }
    }
    
    configureSize(aSpace,hSpace)
    {
        //var minHeight = 100
        
        //this.div.style.height = minHeight + "px"
        
    }
    
    
    computeSize(widget_width)
    {
        var rect = elem.getBoundingClientRect();
        var res = [widget_width, rect[1]]
        return res
    }
    
    draw(ctx, node, widget_width, y, H)
    {
        
        this.configureSize(H,widget_width)
        
    }
    setValue(k,v)
    {
        if (k == this.property)
        {
            for(let i = 0; i < v.length; i++)
            {
                if(i >= this.children.length)
                {
                    this.addTextBox()
                }
                
                
                this.children[i].setValue(i,v[i])
                
                this.value[i] = v[i]
            }
        }
        //this.textarea.value=v
    }
    
    getMinHeight()
    {
        return this.div.offsetHeight;
        var rect = this.div.getBoundingClientRect();
        return rect.height;
    }
}
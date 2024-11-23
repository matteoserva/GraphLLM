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
        if(this.property && this.property == k && this.textarea.value!=v)
        {
            var scrollTop = this.textarea.scrollTop //BUG WORKAROUND:save the scroll before playing with size
            var totally_scrolled = this.textarea.scrollTop >= 5 &&
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

}

class CustomFileDrop {
        constructor(parent,name,options)
    {

        this.div = this.makeElement(parent)
        this.property = options.property
        this.parent = parent
        this.files = []
    }

    makeDropArea()
    {
        var that = this
        var dropArea = document.createElement("div")
        dropArea.className = "dropArea"
        dropArea.style="border: 2px dashed #ccc;  border-radius: 20px; padding: 20px; text-align: center;";
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, preventDefaults, false);
        });

        function preventDefaults(e) {
            e.preventDefault();
            e.stopPropagation();
        }

        ['dragenter', 'dragover'].forEach(eventName => {
            dropArea.addEventListener(eventName, highlight, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            dropArea.addEventListener(eventName, unhighlight, false);
        });

        function highlight(e) {
            dropArea.style.borderColor="purple"
        }

        function unhighlight(e) {
            dropArea.style.borderColor=null
        }

        dropArea.addEventListener('drop', handleDrop, false);

        function handleDrop(e) {
            let dt = e.dataTransfer;
            let files = dt.files;

             ([...files]).forEach(uploadFile)
        }

        function uploadFile(file) {
            let reader = new FileReader();
            reader.onload = function(e) {
                that.addFile(file.name, e.target.result,dropArea)
                that.notifyValue(that,that.property,that.files)
            };
            reader.readAsText(file);
        }

        return dropArea;
    }

    addFile(fileName, fileContent,dropArea) {
            let fileIcon = document.createElement('div');
            fileIcon.className = 'file-icon';
            fileIcon.style="white-space: nowrap"
            fileIcon.innerHTML = `<i class="fas fa-file"> ${fileName} </i><span class="delete-button">Delete</span>`;
            var fileData = {name: fileName, content: fileContent}

            fileIcon.querySelector(".delete-button").addEventListener("click", (event)=>{deleteFile(event,fileData,fileIcon)}, false);
            fileIcon.querySelector(".fas").addEventListener("click", (event)=>{showFile(event,fileData, fileIcon)}, false);
            //fileIcon.addEventListener('click', () => showFileContent(file));
            dropArea.appendChild(fileIcon);
            this.files.push(fileData)

            var that = this
            function deleteFile(el,ref,fileIcon) {
                fileIcon.remove()
                let index = this.files.indexOf(ref);
                if(index !== -1) {
                  that.files.splice(index, 1);
                }
                that.notifyValue(that,that.property,that.files)
            }

            function showFile(el,ref, fileIcon) {
                var textarea = that.div.querySelector(".CustomTextarea")
                textarea.value = ref.content
            }
    }

    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.className = "CustomFileList"
        div.style="min-height: 50px; display: flex; flex-direction:column; height:100%; padding-bottom: 2px; /* background-color: black; */"

        div.appendChild(this.makeDropArea());

        var textOutput = new CustomTextarea(this, "",{property:"ciao"})
        textOutput.appendElement(div)
        textOutput.setValue("ciao","bbb ciao")

        return div
    }

    notifyValue(me, k,val)
    {
        this.parent.notifyValue(this,k,val)
    }

    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }

    setValue(k,v)
    {
        console.log(k,v)
        if(this.property && this.property == k)
        {
            var dropArea = this.div.querySelector(".dropArea")
            v.forEach((element) => this.addFile(element.name,element.content,dropArea))
        }
    }

}

class CustomHtmlCanvas {
        constructor(parent,name,options)
    {
        this.disabled = false
        this.name=name
        this.H = 15
        this.type = "custom"
        this.y=0
        this.div = this.makeElement(parent)

        this.property = options.property
        this.parent = parent
        this.options = {multiline:false}
        this.minHeight = 50
        this.saved_content = null;
    }


    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        var text = document.createElement("iframe")
        div.style="width: 100%; height: 100%; background-color: white; margin-bottom: 4px;"
        text.style="width: 100%; height: 100%"
        text.src = "about:blank"

        div.appendChild(text)
        this.textarea = text
        return div

    }

    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }

    draw(ctx, node, widget_width, y, H)
    {


    }

    configureSize(aSpace,hSpace)
    {


    }

    setValue(k,v)
    {
        if(this.property && this.property == k && v && v.graphllm_type == "output" && this.saved_content != v)
        {
            this.saved_content = v
            var encoded_html = btoa(v)
            this.textarea.src = "data:text/html;charset=utf-8;base64," + encoded_html
            //this.textarea.innerText = v
        }
    }
    getMinHeight()
    {
        return this.minHeight;
    }

}



class CustomTextOutput extends CustomTextCommon{
        constructor(parent,name,options)
    {
        super(parent,name,options)
        this.options = {multiline:false}
        this.minHeight = 50
        this.saved_content = null;
    }

    setDisplayValue(value)
    {
        this.saved_content = value
        this.redrawContent()
    }

    redrawContent(markdown)
    {
        if(this.use_markdown)
        {
            var text = this.saved_content;
            var converter = new showdown.Converter();
			converter.setOption('tables', true);
            var html = converter.makeHtml(text);
            this.textarea.innerHTML = html
        }
        else
        {
            this.textarea.innerText = this.saved_content
        }

    }


    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.className = "CustomTextDiv";
        div.classList.add('deselected');
        var text = document.createElement("div")
        text.className = "nameText";
        text.innerText = this.name

        div.appendChild(text)

        var control= document.createElement("div")
		control.style="color:DarkGray;position:absolute; top:0px; transform: translateY(-100%); right: 0px"
		control.className = "TextControl";
        control.innerHTML = 'Markdown<input type="checkbox"/>'
        var checkbox = control.querySelector("input")
        var that = this
        checkbox.addEventListener("click",function (e) {
            that.use_markdown = checkbox.checked
            that.redrawContent()
            } );
        div.appendChild(control)

        div.style="position:relative";
        div.style.height = "100%";
        div.style.paddingBottom = "4px";

        var textarea = document.createElement("div");
        div.appendChild(textarea)
        textarea.className="CustomTextOutput"
        textarea.tabIndex=0;
        this.textarea = textarea

        textarea.addEventListener("keydown",  function (ev) {
           if (ev.key === 'a' && ev.ctrlKey)
            {
                ev.preventDefault();
                if (document.selection) {
                    var range = document.body.createTextRange();
                    range.moveToElementText(textarea);
                    range.select();
                } else if (window.getSelection) {
                    var range = document.createRange();
                    range.selectNode(textarea);
                    window.getSelection().removeAllRanges();
                    window.getSelection().addRange(range);
                }
            }

         });
        textarea.addEventListener("focusout", function(event){
                    this.textareaUnfocus(textarea)
                     if (window.getSelection) {window.getSelection().removeAllRanges();}
             else if (document.selection) {document.selection.empty();}

        }.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div

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
            //textarea.style.width = "100%";
            //textarea.style.height = "100%";
            textarea.style.minHeight = ""
            textarea.style.minWidth = ""
        }

    }



}

class CustomTextInput extends CustomTextCommon{
    constructor(parent,name,options)
    {
        super(parent,name,options)
        this.options = {multiline:false}
        this.minHeight = 25
    }

    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.className = "CustomInputDiv";
        div.classList.add('deselected');
        var text = document.createElement("div")
        text.className = "nameText";
        text.innerText = this.name

        div.appendChild(text)
        div.style="position:relative";
        div.style.height = this.minHeight +"px";
        div.style.paddingBottom = "4px";

        var textarea = document.createElement("input");
        div.appendChild(textarea)
        textarea.className="CustomTextInput"
        textarea.style='white-space: pre;'
        textarea.style.width = "100%";
        textarea.style.height = this.minHeight +"px";
        this.textarea = textarea

        textarea.addEventListener("focusout", function(event){this.textareaUnfocus(textarea)}.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div

    }





    configureSizeInFocus()
    {
        var textarea = this.textarea
        if (this.inFocus)
        {


        this.textarea.style.whiteSpace="pre"
            textarea.style.width = "1px";


            textarea.style.minWidth = ""

            var minHeight = (textarea.scrollHeight);
            var minWidth = (textarea.scrollWidth);
            textarea.style.width = "100%";
            textarea.style.height = this.minHeight + "px"
            var currentWidth = textarea.clientWidth
            var currentHeight = textarea.clientHeight

            minWidth = Math.min(minWidth,window.innerWidth*0.7)
            minHeight = Math.min(minHeight,window.innerHeight*0.7)

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
            textarea.style.height = this.minHeight +"px";
            textarea.style.minHeight = ""
            textarea.style.minWidth = ""
        }

    }


}

class CustomTextarea extends CustomTextCommon{
        constructor(parent,name,options)
    {
        super(parent,name,options)
        this.options = {multiline:false}
        this.minHeight = 50
    }
    
    
    
    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.className = "CustomTextDiv";
        div.classList.add('deselected');
        var text = document.createElement("div")
        text.className = "nameText";
        text.innerText = this.name
        div.appendChild(text)


        var textarea = document.createElement("textarea");
        div.appendChild(textarea)
        textarea.className="CustomTextarea"
        textarea.style='white-space: pre; padding: ' + this.margin + 'px'

        textarea.style.width = "100%";
        textarea.style.height = "100%";
        this.textarea = textarea

        this.textarea.ondrop = function(e) {
			if(e.dataTransfer && e.dataTransfer.types && e.dataTransfer.types[0] == "Files")
			{
				e.preventDefault(); console.log(e);
				f = e.dataTransfer.items[0].getAsFile()
				var reader = new FileReader();
				reader.onload = function(read) {textarea.value = reader.result}
				reader.readAsText(f)
			}
		}
        this.textarea.ondragover = function(e) {e.preventDefault(); }

        textarea.addEventListener("focusout", function(event){this.textareaUnfocus(textarea)}.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div
        
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

        this.innerDialog.style.height = "min-content"
        var scrollHeight = this.innerDialog.clientHeight
        this.innerDialog.style.height = "100%"

        return [undefined,scrollHeight]
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

    executeAction(action, data)
    {
        if(action.target == "set")
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
            this.notifyValue(this,action.parameter,newValue)
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

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
        this.accumulator = ""
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
            showFile(null,fileData,fileIcon)
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
        textOutput.setValue("ciao","")

        this.showData = function(value)
        {
            textOutput.setValue("ciao",value)
        }

        return div
    }

    notifyValue(me, k,val)
    {
        if(me instanceof CustomTextarea)
        {

            var selectedIndex = this.files.length-1
            var currentFile = this.files[selectedIndex]
            currentFile.content = val
            this.parent.notifyValue(this,this.property,this.files)

        }
        else
        {
            this.parent.notifyValue(this,k,val)
        }
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

    executeAction(eventId, action, data)
    {
        console.log("files action",eventId, action, data)
        if (action.target == "reset")
        {
            this.accumulator = ""
            var textarea = this.div.querySelector(".CustomTextarea")
            this.original = textarea.value

        } else if (action.target == "append")
        {
            this.accumulator += data
            var appended = this.original.replace("{p:fim}", this.accumulator)
            this.showData(appended)


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

function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

function escapeReplacement(string) {
    return string.replace(/\$/g, '$$$$');
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
            var converter = new showdown.Converter({
            extensions: [
              showdownKatex(
                  {
                      displayMode: true,
                      throwOnError: false, // allows katex to fail silently
                      errorColor: '#ff0000',
                      delimiters: [],
                  }
              )]
              }

            );
			converter.setOption('tables', true);
			text = text.replace(/(\s*)\\\[\n([^\n]+)\n\s*\\\]\n/g,'$1<span><code class="latex language-latex">$2</code></span>\n')
			text = text.replace(/(\s|^)\\\(([^\n]+?)\\\)/g,'$1<span><code class="latex language-latex">$2</code></span>')
			text = text.replace(/(\s|^)\\\[([^\n]+?)\\\]/g,'$1<span><code class="latex language-latex">$2</code></span>')
			// \boxed{\int_{\Omega} f \, d\mu = \int_{\Omega} f^+ \, d\mu - \int_{\Omega} f^- \, d\mu}
			text = text.replace(/(^|\n)(\\boxed{[^\n]+})(\n|$)/g,'$1<span><code class="latex language-latex">$2</code></span>$3')
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


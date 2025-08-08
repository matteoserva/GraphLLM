
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

class CustomImageDrop {
    constructor(parent,name,options)
    {
        this.property = options.property
        this.parent = parent
        this.image = {}
        this.div = this.makeElement(parent)
    }

    makeDropArea()
    {
        var that = this
        var dropArea = document.createElement("div")
        dropArea.className = "dropArea"
        dropArea.style="border: 2px dashed #ccc;  border-radius: 2px; padding: 2px; text-align: center;";

        var imageArea = document.createElement("img")
        dropArea.appendChild(imageArea);
        imageArea.style="max-width: 100%";

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
            reader.onloadend = function(e) {
                that.addFile(file.name, e.target.result,dropArea)
                that.image = {name: file.name, content: e.target.result}
                that.notifyValue(that,that.property,that.image)
            };
            reader.readAsDataURL(file);
        }

        return dropArea;
    }

    addFile(fileName, fileContent,dropArea) {
        var imageArea = dropArea.querySelector("img")
        imageArea.src = fileContent;
    }

    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");
        div.className = "CustomImageArea"
        div.style="min-height: 50px; display: flex; flex-direction:column; height:100%; padding-bottom: 2px; /* background-color: black; */"

        div.appendChild(this.makeDropArea());

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
        if(this.property && this.property == k)
        {
            this.image = v
            var imageArea = this.div.querySelector("img")
            imageArea.src = v.content;

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

        textarea.addEventListener("focusout", function(e){ this.handleFocusOutEvent(e,textarea)}.bind(this))
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

        textarea.addEventListener("focusout", function(e){ this.handleFocusOutEvent(e,textarea)}.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div
        
		
    }
    
	
    
    configureSizeInFocus()
    {
        var textarea = this.textarea.cloneNode(true)
        textarea.style.visibility="hidden"
        document.querySelector(".litegraph .content").append(textarea)
        if (this.inFocus)
        {
            var oldScrollTop = this.textarea.scrollTop
        
            textarea.style.whiteSpace="pre"
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
            this.textarea.style.minHeight = (minHeight+10) + "px"
            this.textarea.style.minWidth = (minWidth+15)  + "px"
            textarea.style.whiteSpace="pre-wrap";

            var newScrollTop = this.textarea.scrollTop;
            if (newScrollTop < oldScrollTop)
            {
                this.textarea.scrollTop = oldScrollTop;
            }

        }

        textarea.remove();
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


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
							event.target.focus()
							
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

class CustomToolSelector {
        constructor(parent,name,options)
    {
        this.disabled = false
        this.name=name
        this.H = 15
        this.type = "custom"
        this.y=0
        this.tools_list = this.initToolsList(options.tools_list)
        this.div = this.makeElement(parent)



        this.property = options.property
        this.parent = parent
        this.options = {multiline:false}
        this.minHeight = 50
        this.saved_content = null;

        this.updateCategoryView()
        this.updateParent()
    }

    initToolsList(tools_list_data)
    {
        let tools_list = {}
        for (let category in tools_list_data)
        {
            tools_list[category] = {}
            for (let i in tools_list_data[category])
            {
                let tool_name = tools_list_data[category][i]
                let defaultEnabled = category == "answer"
                tools_list[category][tool_name] = {enabled: defaultEnabled}
            }
        }
        return tools_list
    }

    updateCategoryCounter(category_name)
    {
        let category_counter = 0
        let disabled_counter = 0
        for (let tool in this.tools_list[category_name])
        {
            if(this.tools_list[category_name][tool].enabled)
            {
                category_counter += 1;
            }
            else
            {
                disabled_counter += 1;
            }
        }
        let category_nodes = Array.from(this.div.querySelectorAll(".category"))
        let filtered_node = category_nodes.filter((c) => c.dataset.category == category_name)[0];
        let node = filtered_node.querySelector(".category-counter")
        node.innerText = category_counter
        if(category_counter > 0)
        {
            if(disabled_counter > 0)
            {
                node.style.backgroundColor = "#404000"
            }
            else
            {
                node.style.backgroundColor = "#004000"
            }
        }
        else
        {
            node.style.backgroundColor = null;
        }
    }

    collapseCategories()
    {
        this.div.querySelectorAll('.category-header').forEach(header => {

            const toolsDiv = header.nextElementSibling;
            let wasVisible = toolsDiv.style.display === 'block'
            if(wasVisible)
            {
                toolsDiv.style.display = 'none';
                header.classList.remove("focused")
            }
        });

    }

    makeElement(parentNode)
    {
        var dialog = parentNode
        var div = document.createElement("div");


        div.className = "tool-selection"




        var innerHTML= ""
        for (let category in this.tools_list) {
            let tools = this.tools_list[category]


            let h = ""
            for (let tool in tools)
            {
                h += '<div class="tool" data-tool-name="' + tool + '">' + tool + '</div>\n';
            }
            let html = `
            <div class="category" data-category="` + category + `">
                      <div class="category-header"><span class="category-title">` + category + `</span><span class="category-counter">0</span></div>
                      <div class="tool-selection-tools">` + h + `
                      </div>
                </div>
            `
            innerHTML += html;
        }





        div.innerHTML = innerHTML
        div.querySelectorAll('.category-header').forEach(header => {
          header.addEventListener('click', () => {
            const toolsDiv = header.parentNode.querySelector(".tool-selection-tools");
            let wasVisible = header.parentNode.classList.contains("focused")
            if(!wasVisible)
            {
                this.collapseCategories()
            }

            //toolsDiv.style.display = wasVisible ? 'none' : 'block';
            if(wasVisible)
            {
                header.parentNode.classList.remove("focused")
            }
            else
            {
                header.parentNode.classList.add("focused")
                let top = header.parentNode.parentNode.scrollTop
                toolsDiv.style.transform = "translate(0,-" + top + "px)"
            }
          });
        });

        div.querySelectorAll('.category').forEach(header => {
          header.tabIndex=0;
          const toolsDiv = header.querySelector(".tool-selection-tools");
          header.addEventListener('focusout', (e) => {
            if(!(e.relatedTarget && e.relatedTarget.className == "category"))
               toolsDiv.style.display = 'none'

            header.classList.remove("focused")
          });
          header.addEventListener('focusin', (e) => {
            //header.classList.add("focused")
          });

        });
        /*div.querySelectorAll('.tool-selection .tool-selection-tools').forEach(header => {
          header.parentNode.addEventListener('mouseleave', () => {
            header.style.display = 'none';
          });
        });*/
        div.querySelectorAll('.category').forEach(categoryNode => {
            categoryNode.querySelectorAll('.tool').forEach(header => {
                    let tool = header.dataset.toolName
                    let category = categoryNode.dataset.category
                    this.tools_list[category][tool].node = header
                  header.addEventListener('click', () => {
                    let becomeActive = !header.classList.contains("selected")
                    if(!becomeActive)
                    {
                        header.classList.remove("selected")
                    }
                    else
                    {
                        header.classList.add("selected")
                    }

                    this.tools_list[category][tool].enabled = becomeActive
                    this.updateCategoryCounter(category)
                    this.updateParent()
                  });
            });
        });

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

    updateParent()
    {
        let val = {}
        for(let cat in this.tools_list)
        {
            val[cat] = {}
            for (let tool in this.tools_list[cat])
            {
                let el = {}
                el.enabled = this.tools_list[cat][tool].enabled
                val[cat][tool] = el
            }
        }
        this.parent.notifyValue(this,this.property,val)

    }

    updateCategoryView()
    {
        for (let cat in this.tools_list)
        {
            for (let tool in this.tools_list[cat])
            {
                if(!this.tools_list[cat][tool].enabled)
                {
                    this.tools_list[cat][tool].node.classList.remove("selected")
                }
                else
                {
                    this.tools_list[cat][tool].node.classList.add("selected")
                }
            }
            this.updateCategoryCounter(cat)
        }

    }

    setValue(k,v)
    {
        if(this.property && this.property == k && v &&  this.saved_content != v)
        {
            ;
        }
        else
        {
            return;
        }
        for (let cat in v)
        {
            if (!(cat in this.tools_list))
            {
                continue;
            }
            for (let tool in v[cat])
            {
                if(!(tool in this.tools_list[cat]))
                {
                    continue;
                }
                this.tools_list[cat][tool].enabled = v[cat][tool].enabled;

            }

        }
        this.updateCategoryView()

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
        this.saved_content = "";
        this.config={use_markdown: false}
    }

    setDisplayValue(value)
    {
        this.saved_content = value
        this.redrawContent()
    }

	cleanHtmlEmptyNodes(children)
	{
		   /* if the node contains only one real child and two empty text nodes,
           then it is a formatting issue in showdownjs. remove the empty nodes.
           The empty texts are incompatible with the white-space: pre property */


        var textChildren = Array.from(children).filter((el) => el.nodeName == "#text");

        var emptyChildren = textChildren.filter((el) => el.textContent.trim() == "");

        var numNodes = children.length
        var numText = textChildren.length
        var numEmpty = emptyChildren.length

        if(numText > 0 && numEmpty == numText && numNodes > numText)
        {
            //textChildren.map((el) => el.remove())
        }

        var fathers = Array.from(children).filter((el) => el.childNodes.length > 0);
        fathers.map((el) => this.cleanHtmlEmptyNodes(el.childNodes));

        if(numText == 2 && numEmpty == numText && numNodes == 3)
        {
            textChildren.map((el) => el.remove())
        }
		
	}

	cleanHtmlCodeBlocks(textarea)
	{
		//<p style="position: absolute; top: 0px; right:0px">ciao</p>
		var codeBlocks = textarea.querySelectorAll("pre > code[class*='language-']")
		codeBlocks.forEach((element) => appendType(element));
		
		function appendType(el)
		{
			var p = document.createElement("p");
			p.style="position: absolute; margin: 0px; top: -0px; right:10px; transform: translateY(-50%); background-color: #202020; border-radius: 4px; padding: 1px; color: darkgray; user-select:none"
			var className = el.className.match("language-(.*)")[1]
			p.innerHTML = className;
			el.parentElement.appendChild(p)
			el.parentElement.style.marginTop = "4px"
			el.parentElement.style.marginBottom = "4px"
			el.parentElement.style.paddingTop = "4px"
			el.parentElement.style.paddingBottom = "4px"
			el.parentElement.style.position = "relative"
		}
		
		return 0;
	}

    cleanHtml(textarea)
    {
		
		var children = textarea.childNodes;
		var inner = textarea.innerHTML

		inner = inner.replace(/\<blockquote\>\n(\s+\<)/g,"<blockquote>$1") //blockquote\n  <p>
        //inner = inner.replace(/\n(\s*)\<\/blockquote\>/g,"$1</blockquote>") //blockquote\n  <p>
       /* inner = inner.replace(/\<\/li\>\n/g,"</li>")
        inner = inner.replace(/\<\/p\>\n/g,"</p>")
        inner = inner.replace(/\<\/blockquote\>\n/g,"</blockquote>")
        inner = inner.replace(/\<ul\>\n/g,"<ul>")*/
        inner = inner.replace(/\<\/([a-zA-Z0-9]+)\>\n/g,"</$1>")
        inner = inner.replace(/\<(hr)\>\n/g,"<$1>")
        inner = inner.replace(/\<(br)\>\n/g,"<$1>")
		//inner = inner.replace(/\>[\n\r]+\</g,"><")
		//inner = inner.replace(/blockquote\>\n(\s+\<)/g,"blockquote>$1") //blockquote\n  <p>
		//inner = inner.replace(/\>\n\s\s\</g,"><")
		//inner = inner.replace(/\<blockquote>[\n\r\s]+\</g,"<blockquote><")
		textarea.innerHTML = inner
		//this.cleanHtmlEmptyNodes(children)
		this.cleanHtmlCodeBlocks(textarea)
        return 0;
    }

    redrawContent(markdown)
    {
        var scrollTop = this.textarea.scrollTop //BUG WORKAROUND:save the scroll before playing with size
        var totally_scrolled = this.textarea.scrollTop >= 5 &&
            (Math.abs(this.textarea.scrollHeight - this.textarea.clientHeight - this.textarea.scrollTop) <= 1);
        if(this.config.use_markdown)
        {
            var text = this.saved_content;
            var converter = new showdown.Converter({
            extensions: [
              showdownKatex(
                  {
                      displayMode: true,
                      throwOnError: false, // allows katex to fail silently
                      errorColor: '#ff0000',
                      delimiters: [{ left: "$", right: "$", display: false }],
                  }
              )]
              }

            );
			converter.setOption('tables', true);
			converter.setOption('disableForced4SpacesIndentedSublists', true)
			text = text.replace(/(\s*)\\\[\n([^\n]+)\n\s*\\\](\n|$)/g,'$1<span><code class="latex language-latex">$2</code></span>\n')
			text = text.replace(/(\s|^)\\\(([^\n]+?)\\\)/g,'$1<span><code class="latex language-latex">$2</code></span>')
			text = text.replace(/(\s|^)\\\[([^\n]+?)\\\]/g,'$1<span><code class="latex language-latex">$2</code></span>')

			/*
                \[
                a
                b
                \]
			*/
			text = text.replace(/(\s|^)\\\[\n(([^\n]+\n){1,5})\\\]/g,'$1<span><code class="latex language-latex">$2</code></span>')


			// \boxed{\int_{\Omega} f \, d\mu = \int_{\Omega} f^+ \, d\mu - \int_{\Omega} f^- \, d\mu}
			text = text.replace(/(^|\n)(\\boxed{[^\n]+})(\n|$)/g,'$1<span><code class="latex language-latex">$2</code></span>$3')
            var d = document.createElement("div")
			d.innerHTML = text
			var t = d.querySelector("think")
			if(t)
			{
				
				var d2 = document.createElement("div")
				d2.className = "thinking"
				d2.innerHTML = t.innerHTML.trim()
				
				
				var dc = document.createElement("div")
				dc.className = "thinking-container"
				dc.style = "background-color: #202020"
				dc.style.marginTop = "4px"
				dc.style.marginBottom = "4px"
				dc.style.paddingTop = "4px"
				dc.style.paddingBottom = "4px"
				dc.style.position = "relative"
				
				
				var p = document.createElement("p");
				p.style="position: absolute; margin: 0px; top: -8px; right:10px; background-color: #202020; border-radius: 4px; padding: 1px; color: darkgray; user-select:none"
				p.innerHTML = "Think"
				
				dc.appendChild(d2)
				dc.appendChild(p)
				
				t.replaceWith(dc)
				
				text = unEscape(d.innerHTML)

				function unEscape(htmlStr) {
                    htmlStr = htmlStr.replace(/&lt;/g , "<");
                    htmlStr = htmlStr.replace(/&gt;/g , ">");
                    htmlStr = htmlStr.replace(/&quot;/g , "\"");
                    htmlStr = htmlStr.replace(/&#39;/g , "\'");
                    htmlStr = htmlStr.replace(/&amp;/g , "&");
                    return htmlStr;
                }

			}
			
			var html = converter.makeHtml(text);
            this.textarea.innerHTML = html
            this.cleanHtml(this.textarea)

        }
        else
        {
            this.textarea.innerText = this.saved_content
        }
        if(totally_scrolled)
        {
            this.textarea.scrollTo(0,this.textarea.scrollHeight)
        }
        else
        {
            this.textarea.scrollTop = scrollTop
        }

    }

    setConfig(config, notify=false)
    {
        if ("use_markdown" in config)
        {

            this.config.use_markdown = config.use_markdown
            if(config.use_markdown)
            {
		this.textarea.classList.remove("markdown_off")
		this.textarea.classList.add("markdown_on")
	    }
            else
            {
		this.textarea.classList.remove("markdown_on")
		this.textarea.classList.add("markdown_off")
	    }
            this.redrawContent()

        }
        if(notify)
        {
            this.parent.notifyValue(this,this.property,this.config)
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
		control.style="color:DarkGray;position:fixed; top:0px; transform: translateY(-100%); right: 0px"
		control.className = "TextControl";
        control.innerHTML = 'Markdown<input type="checkbox"/>'
        var checkbox = control.querySelector("input")
        var that = this
        checkbox.addEventListener("click",function (e) {
            that.setConfig({use_markdown: checkbox.checked}, true)

            } );
        div.appendChild(control)

        div.style="position:relative";
        div.style.height = "100%";
        div.style.paddingBottom = "4px";

        var textarea = document.createElement("div");
        div.appendChild(textarea)
        textarea.className="CustomTextOutput"
        textarea.classList.add("markdown_off")
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
        textarea.addEventListener("focusout", function(e){ this.handleFocusOutEvent(e,textarea)}.bind(this))
        textarea.addEventListener("focusin", function(event){this.textareaFocus(textarea)}.bind(this))
        textarea.addEventListener("keyup", function(event){this.textChange()}.bind(this))
        return div

    }

	textareaUnfocus(textarea)
	{
		super.textareaUnfocus(textarea)
		if (window.getSelection) {window.getSelection().removeAllRanges();}
             else if (document.selection) {document.selection.empty();}
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
        else
        {
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

    setValue(k,v)
    {
        if(typeof v == "object")
        {
            this.setConfig(v,false)
            var checkbox = this.div.querySelector("input[type='checkbox']")
            checkbox.checked = this.config.use_markdown
        }
        else
        {
            super.setValue(k,v)
        }

    }

    executeAction(eventId, action, data)
    {

        if (action.target == "set")
        {
            this.saved_content = data
            this.redrawContent()

        } else if (action.target == "reset")
        {
            this.saved_content = ""

        } else if (action.target == "append")
        {
            this.saved_content += data
            this.redrawContent()
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


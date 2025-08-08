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
        this.old_content = "";
        this.config={use_markdown: false}
        this.lastRedrawTimestamp = 0;
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

    cleanKatexBlocks(katexSpan)
    {
        var prevSibling = katexSpan.previousSibling || {}
        var nextSibling = katexSpan.nextSibling || {}
        var parentCount = katexSpan.parentElement.childElementCount

        if(prevSibling.nodeType == Node.TEXT_NODE  && nextSibling.nodeType == Node.TEXT_NODE  )
        {
            if(prevSibling.textContent.trim() == "$$" && nextSibling.textContent.trim() == "$$")
            {
                prevSibling.remove()
                nextSibling.remove()
            }
            console.log("clean?")
        }
    }

    cleanHtml(textarea)
    {

		var children = textarea.childNodes;
        var katexNodes = textarea.querySelectorAll("span > span.katex-display")
        katexNodes.forEach((element) => this.cleanKatexBlocks(element.parentNode));

        var inner = textarea.innerHTML

        // remove newlines after some html tags, they break <pre> formatting
		inner = inner.replace(/\<blockquote\>\n(\s+\<)/g,"<blockquote>$1") //blockquote\n  <p>
        inner = inner.replace(/\<\/(?!strong)([a-zA-Z0-9]+)\>\n/g,"</$1>") //negative lookahead
        inner = inner.replace(/\<(hr)\>\n/g,"<$1>")
        inner = inner.replace(/\<(br)\>\n/g,"<$1>")

		textarea.innerHTML = inner
		//this.cleanHtmlEmptyNodes(children)
		this.cleanHtmlCodeBlocks(textarea)
        return 0;
    }


	convertToMarkdown(original_text)
	{
		var text = original_text
		let katex = showdownKatex(
                      {
                          displayMode: true,
                          throwOnError: true, // allows katex to fail silently
                          errorColor: '#ff0000',
                          delimiters: [{ left: "$$\n", right: "$$", display: true }, { left: "$ ", right: " $", display: false } ],
                      }
                  )()
                katex[0].type = "lang"

                let katexFixer = [
                    {
                      type: 'lang',
                      filter(html = '') {
                        let  d = document.createElement("div")
                        d.innerHTML = html
                        // fixes #### Second Term: $ 2\pi H \sqrt{\frac{V}{\pi H}} $
                        d.querySelectorAll("path").forEach( (element) => {element.remove()})
						d.querySelectorAll("annotation").forEach( (element) => {element.remove()})
						d.querySelectorAll("span.katex-html").forEach( (element) => {element.remove()})
                        let r = d.innerHTML
                        return r;
                      },
                    },
                ];

                var converter = new showdown.Converter({
                extensions: [] //[katex,katexFixer]
                  }

                );
                converter.setOption('tables', true);
                converter.setOption('disableForced4SpacesIndentedSublists', true)


                // replace inline $$ ... $$ with $ ... $
                text = text.replace(/\$\$ ([^\n]+) \$\$/g,'$ $1 $')

				// replace $r$ with $ r $
				text = text.replace(/\$(\w)\$/g,'$ $1 $')

                // replace inline $...$ with $ ... $   offender: - $H = 16 \text{ cm}$
                text = text.replace(/\$(\S[^\n]+(\\text\{|\\boxed\{)[^\n]+\S)\$/g,'$ $1 $')

				text = text.replace(/\$ ([^\n]+) \$/g,(match,p1) => katexFixer[0].filter(katex[0].filter(match)) )
				text = text.replace(/\$\$\n([^\n]+\n)+?\s*\$\$(\n|$)/g,(match,p1) => katexFixer[0].filter(katex[0].filter(match)) )

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

					dc.appendChild(p)
                    dc.appendChild(d2)


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
				return html
	}

    redrawContent(forceRedraw = false)
    {
        var scrollTop = this.textarea.scrollTop //BUG WORKAROUND:save the scroll before playing with size
        var totally_scrolled = this.textarea.scrollTop >= 5 &&
            (Math.abs(this.textarea.scrollHeight - this.textarea.clientHeight - this.textarea.scrollTop) <= 1);

        if( this.old_content === this.saved_content && this.old_markdown === this.config.use_markdown && !forceRedraw )
        {
            return;
        }

        if(this.old_content.length > 100 && this.saved_content.length > this.old_content.length && this.saved_content.startsWith(this.old_content))
        {
                var diffContent =  this.saved_content.substring(this.old_content.length)
        }

        this.old_content = this.saved_content
        this.old_markdown = this.config.use_markdown


        const now = Date.now();

        if(diffContent && this.config.use_markdown && (now-this.lastRedrawTimestamp)< 500)
        {
			let currentNode = this.textarea
			let lastTextNode = currentNode;
			while ((currentNode = currentNode.lastChild)) {
				  lastTextNode = currentNode;
			}
			if (lastTextNode.nodeType == Node.TEXT_NODE)
			{
				lastTextNode.nodeValue += diffContent;
			}
			else
			{
				lastTextNode.innerHTML += diffContent;
			}

        }
        else if(this.config.use_markdown)
        {
                this.lastRedrawTimestamp = now

                var text = this.saved_content;
                var html = this.convertToMarkdown(text)
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
        /*if (this.inFocus)
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
        }*/
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

            this.redrawContent(true)

        } else if (action.target == "reset")
        {
            this.saved_content = ""
            this.old_content = ""

        } else if (action.target == "append")
        {
            this.saved_content += data
            this.redrawContent()
        }
    }

}
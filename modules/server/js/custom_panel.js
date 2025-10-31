
class CustomWidgetsContainer {
    constructor(parent,name,options)
    {
        this.children = []
    }

    addWidget(type, name, options)
    {
        if(type == "list")
        {
            var elem = new CustomList(this, name,options)
        }
        else if(type=="text_input")
        {
            var elem = new CustomTextInput(this, name,options)
        }
        else if(type=="text_output")
        {
            var elem = new CustomTextOutput(this, name,options)
        }
        else if(type=="html_canvas")
        {
            var elem = new CustomHtmlCanvas(this, name,options)
        }
        else if(type=="file_drop")
        {
            var elem = new CustomFileDrop(this, name,options)
        }
        else if(type=="image_drop")
        {
            var elem = new CustomImageDrop(this, name,options)
        }
        else if(type=="tools_selector")
        {
            var elem = new CustomToolSelector(this, name,options)
        }
		else if(type=="panel")
        {
            var elem = new CustomPanel(this, name,options)
        }
        else if(type=="toggle")
        {
            var elem = new CustomToggle(this, name,options)
        }
        else
        {
            var elem = new CustomTextarea(this, name,options)
        }
        this.children.push(elem)
        return elem
    }

}




class CustomPanel extends CustomWidgetsContainer{
        constructor(parent,name,options)
    {
        super(parent,name,options)
        this.disabled = false
        this.name=name
        this.H = 15
        this.type = "panel"
        this.y=0
        this.div = this.makeElement()
        this.property = options.property
        this.properties = {}

        this.parent = parent
    }


    makeElement()
    {
        var div = document.createElement("div");
		div.className = "CustomPanelDiv";
        div.classList.add('deselected');
        div.tabIndex = "0"

		var innercontainer = document.createElement("div");
		innercontainer.className = "div-innercontainer";

		this.innercontainer = innercontainer

		const header = document.createElement('div');
		header.className = 'CustomPanelHeader';
        //div.addEventListener("focusin", function(e){ div.classList.add('selected'); div.classList.remove('deselected');})
        div.addEventListener("focusout", function(e) {
            console.log("div event blur ", e.relatedTarget);
            if (!div.contains(e.relatedTarget)) {
                div.classList.add('deselected');
                div.classList.remove('selected');
            }
        });

        header.addEventListener("click", function(e) {
            console.log("header click. was selected: " , div.classList.contains("selected"))
                if(div.classList.contains("selected"))
                {
                    div.classList.add('deselected');
                    div.classList.remove('selected');
                }
                else
                {
                    div.classList.add('selected');
                    div.classList.remove('deselected');
                }

        });

		const titleSpan = document.createElement('span');
		titleSpan.className = 'CustomPanelTitle';
		titleSpan.textContent = this.name;               // <-- your title text

        const configSpan = document.createElement('span');
		configSpan.className = 'CustomPanelConfig';
		configSpan.textContent = "{}";

        const titleDiv = document.createElement('div');
		titleDiv.className = 'CustomPanelTitleDiv';

		header.appendChild(configSpan)
        header.appendChild(titleSpan)


		const titleArrow = document.createElement('span');
		titleArrow.className = 'CustomPanelArrow';
		titleArrow.textContent = "▼";               // <-- your title text

		header.appendChild(titleDiv);
		header.appendChild(titleArrow);
		div.appendChild(header);
		div.appendChild(innercontainer);

        return div

    }

    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }

    setConfigDisplay(val)
    {
        let o = this.div.querySelector(".CustomPanelConfig")
        const newObj = {}; // Create a new empty object

        for (const key in val) {
              const value = val[key];
              if (value !== "" && value !== false) {
                newObj[key] = value;
              }
        }

        let text = JSON.stringify(newObj, null, " ").replaceAll("\n"," ")
        o.innerText = text
    }


    notifyValue(me, k,val)
    {
        var oldConfig = JSON.stringify(this.properties)
		this.properties[k] = val
		var newConfig = JSON.stringify(this.properties)
		if( newConfig != oldConfig)
		{
            this.parent.notifyValue(this, this.property,this.properties)
            this.setConfigDisplay(this.properties)
        }

    }

    draw(ctx, node, widget_width, y, H)
    {


    }

    configureSize(aSpace,hSpace)
    {


    }

    setValue(k,v)
    {
        if (k == this.property)
        {
            this.properties = v;
            for (const [key, value] of Object.entries(v)) {
              for (const listener of this.children) {
                listener.setValue(key, value);
              }
            }
            this.setConfigDisplay(v)
        }
    }

    getMinHeight()
    {
        return this.minHeight;
    }

    addWidget(type, name, options)
    {
        var elem = super.addWidget(type,name,options)
        elem.appendElement(this.innercontainer )
        return elem
    }

}


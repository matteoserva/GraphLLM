
class TitlebarContainer {
	constructor(parent)
    {
        this.disabled = false
        this.name="CParameters"
        this.value=""

        this.type = "custom"
        this.options = {}
        this.parent = parent

        var oldRemoved = this.parent.onRemoved
        this.parent.onRemoved = function()
        {
			if(oldRemoved)
				oldRemoved.apply(this.parent)
            this.remove()
        }.bind(this)


        
        var oldCollapse = this.parent.collapse.bind(this.parent)
        this.parent.collapse = function()
        {
            oldCollapse()
            this.onCollapse()
        }.bind(this)
		
		var oldonDrawTitleBar = this.parent.onDrawTitleBar
        this.parent.onDrawTitleBar = function()
        {
			if(oldonDrawTitleBar)
				oldonDrawTitleBar.apply(this.parent)
            this.onDrawTitleBar()
        }.bind(this)

		this.makeElement()
		
		// visibility handling
		var visibilityContainer = parent.onVisibilityChange || []
		visibilityContainer.push(this.onVisibilityChange.bind(this))
		parent.onVisibilityChange = visibilityContainer
		
		this.parent_visible = false
    }

	addWidget(type,data)
	{
	    let titledialog = this.dialog.querySelector(".titlebar-dialog");
	    if (type == "brief" || type == "fulldoc")
	    {
	        let newDiv = document.createElement("div");
	        newDiv.className = type;
	        newDiv.innerText = data
	        titledialog.appendChild(newDiv);
	        if (type == "fulldoc")
            {
                newDiv.style.display="none";
                this.dialog.querySelector(".titlebar-header .titlebar-question").style.display=null;
            }
	    }

	}

	makeElement()
    {

        var dialog = document.createElement("div");
        dialog.className = "titlebar-container";
        dialog.style= "position: absolute"
        dialog.innerHTML = `
		<div class="titlebar-header" style="height: ` + LiteGraph.NODE_TITLE_HEIGHT + `px;">
			<div class="titlebar-buttons">

				<div class="titlebar-rotate">🔃<!--<img src="img/rotation.jpg" style="vertical-align: middle; width: 10px; height: 10px"></img>--></div>
				<div class="titlebar-question" style="display: none;">❓</div>
				<div class="titlebar-delete">❌</div>


			</div>
			<img class="titlebar-toggle" src="img/circle.png" style="vertical-align: middle; width: 10px; height: 10px"></img></div>
        <div class="titlebar-dialog"></div>`




		let titleheader = dialog.querySelector(".titlebar-toggle");
		titleheader.addEventListener('click', () => {
            let wasVisible = dialog.classList.contains("focused")
            //titledialog.style.display = wasVisible ? 'none' : 'block';
            if(wasVisible)
			{
				dialog.classList.remove("focused")
			}
			else
			{
				dialog.classList.add("focused")
			}
        });
		dialog.querySelector(".titlebar-delete").addEventListener('click', () => {
            this.parent.graph.remove(this.parent);
        });
        dialog.querySelector(".titlebar-rotate").addEventListener('click', (event) => {
            this.parent.rotateClockwise();
            /*event.stopPropagation();
            event.preventDefault();*/
        });
        dialog.querySelector(".titlebar-question").addEventListener('click', () => {
            dialog.querySelector(".titlebar-dialog > .fulldoc").style.display = "block"
        });
		dialog.tabIndex=0;
		dialog.addEventListener('focusout', () => {
            //titledialog.style.display = "none"; 
			dialog.classList.remove("focused")
        });
		
		
		setTimeout(function(){
            if(this.parent.id)
			{
				var canvas = this.parent.graph.list_of_graphcanvas[0]
				canvas.canvas.parentNode.appendChild(dialog);
			}
        }.bind(this) );
		this.dialog = dialog
    }
	
	computeSize(widget_width)
	{
			return [undefined,-4];
	}
	
	onDrawTitleBar( ctx, title_height, size, scale, fgcolor )
	{
		var node = this.parent;
		var canvas = node.graph.list_of_graphcanvas[0];
		var scale = canvas.ds.scale
		var width = this.parent.flags.collapsed? node._collapsed_width-3 :node.size[0]
        var posX = node.pos[0] + width -2  + canvas.ds.offset[0]
        var posY = node.pos[1] - LiteGraph.NODE_TITLE_HEIGHT  + 0.2 + canvas.ds.offset[1]
        posX *= scale
        posY *= scale
        this.dialog.style.left = posX + "px";
        this.dialog.style.top  = Math.round(posY) + "px";
        //this.dialog.style.width = (node.size[0]-30) + "px";
		//this.dialog.style.height = LiteGraph.NODE_TITLE_HEIGHT + "px"
        this.dialog.style.transform = "scale(" + canvas.ds.scale + ") translateX(-100%)"
        this.dialog.style.transformOrigin = "top left"
	}
	
	
	processVisibilityChange()
	{
		var is_visible = this.parent_visible && !this.parent.flags.collapsed;
		if(is_visible)
        {
			this.dialog.style.display =""
            
        }
        else
        {
            this.dialog.style.display ="none"
        }
	}

	onVisibilityChange(isVisible)
	{
		this.parent_visible = isVisible
		this.processVisibilityChange()
	}

    onCollapse()
    {
        var collapsed = this.parent.flags.collapsed
        this.processVisibilityChange()

    }
	
	remove()
    {
        if(this.dialog)
        {
            this.dialog.remove()
        }
    }
}

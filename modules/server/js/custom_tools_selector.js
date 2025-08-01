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
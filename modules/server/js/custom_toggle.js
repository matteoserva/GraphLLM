
class CustomToggle{
     constructor(parent,name,options)
    {
        this.disabled = false
        this.name=name
        this.type = "toggle"
        this.div = this.makeElement()
        this.property = options.property
        this.parent = parent
    }


    makeElement()
    {
        var div = document.createElement("div");
		div.className = "CustomToggleDiv";
        const titleSpan = document.createElement('span');
		titleSpan.className = 'CustomToggleTitle';
		titleSpan.textContent = this.name;

		const buttonSpan = document.createElement('span');
		buttonSpan.className = 'CustomToggleButton';
        buttonSpan.innerHTML = '<label class="switch"><input type="checkbox"><span class="slider round"></span></label>'

		div.appendChild(titleSpan);
		div.appendChild(buttonSpan);

        this.checkbox = div.querySelector('input[type="checkbox"]');
        this.checkbox.addEventListener('change', (event) => {
            this.notifyValue(event.target.checked);
        });
		// TODO: when the checked status is changed, call notifyValue
        return div

    }

    appendElement(dialog)
    {
        dialog.appendChild(this.div);
    }


    notifyValue(val)
    {
        console.log("The new status of the checkbox: ", val)
        this.parent.notifyValue(this, this.property,val)
    }

    setValue(k,v)
    {
        if (k == this.property)
        {
            this.checkbox.checked = Boolean(v);
        }
    }



}


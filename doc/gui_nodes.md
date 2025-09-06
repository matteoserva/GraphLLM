# GUI node development

## connections

```
builder._addInput("send","string");
```

```
builder._addOutput("receive","string");
```

```
builder._setConnectionLimits({"max_outputs": 3, "min_outputs": 3, "min_inputs": 3})
```

## widgets

#### text input
```
builder._addCustomWidget("textarea", "widget name", {"property": "textarea_identifier"})
```

#### textarea
```
builder._addCustomWidget ("text_input","address",{ "property": "address"})
```

#### number
```
options = { "min": 1, "max": 65535, "step": 10, "precision": 0, "property": "port" }
builder._addStandardWidget("number","port", 8765, None, options )
```

#### combo
```
builder._addStandardWidget("combo", "Agent", "ReAct(xml)", None, {"property": "agent_type", "values": ["ReAct(xml)"]})
```

```
builder._setCallback("onExecute", """function(){var val =this.getInputData(0); if(val) this.container.setValue("parameters",""+val)}""")

source_location = {"position": "input", "slot": 0}
        eventId = {"type": "output"};
        action = {"type": "widget_action", "target": "set", "property": "parameters", "silent": True}
        builder._subscribe(source_location, eventId, action)

source_location = {"position": "input", "slot": 0}
        eventId = {"type": "starting"};
        action = {"type": "widget_action", "target": "reset", "property": "parameters"}
        builder._subscribe(source_location, eventId, action)
```

builder._addSimpleProperty("template", "")
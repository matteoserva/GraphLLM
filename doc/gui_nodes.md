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

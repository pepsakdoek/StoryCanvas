from nicegui import ui
from ..models import AttributeType

def get_templates(gui, etype):
    mapping = {
        "Actor": gui.state.settings.actor_attributes,
        "Place": gui.state.settings.place_attributes,
        "Item": gui.state.settings.item_attributes,
        "Knowledge": gui.state.settings.knowledge_attributes,
        "Event": gui.state.settings.event_attributes
    }
    return mapping.get(etype, [])

def fill_attr_container(gui, etype, container, form):
    templates = get_templates(gui, etype)
    with container:
        for t in templates:
            if t.enabled:
                val = form['attributes'].get(t.name, '')
                label = f"{t.name}{' *' if t.required else ''}"
                
                if t.attr_type == AttributeType.NUMBER:
                    ui.number(label, value=val, 
                              on_change=lambda e, n=t.name: form['attributes'].update({n: str(e.value)})
                             ).props('dense outlined')
                elif t.attr_type == AttributeType.SELECT:
                    ui.select(t.options, label=label, value=val, 
                              on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})
                             ).props('dense outlined').classes('w-full')
                else: # TEXT
                    ui.input(label, value=val, 
                             on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})
                            ).props('dense outlined')

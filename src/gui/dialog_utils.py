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
                             ).props('dense outlined').classes('w-full').props(f'id=attr-number-{t.name}')
                elif t.attr_type == AttributeType.SELECT:
                    # Ensure the current value is valid for the options list to avoid NiceGUI crash
                    val = form['attributes'].get(t.name)
                    if val not in t.options:
                        if val: # It has a value but it's not in options (maybe custom)
                            t.options.append(val)
                        else: # It's empty/None
                            val = None

                    def handle_change(e, n=t.name, f=form):
                        f['attributes'].update({n: e.value})

                    # If allow_custom is enabled, we allow users to type new values
                    sel = ui.select(t.options, label=label, value=val, on_change=handle_change).props('dense outlined').classes('w-full').props(f'id=attr-select-{t.name}')

                    if t.allow_custom:
                        def handle_new_value(e, templ=t, f=form, s=sel):
                            val = e.value
                            if val not in templ.options:
                                templ.options.append(val)
                                s.options = list(templ.options) # Trigger UI update
                                s.update()
                            f['attributes'].update({templ.name: val})
                            s.value = val
                        
                        sel.on_new_value(handle_new_value)
                        sel.props('use-input fill-input hide-selected') # allow typing and hide selected to show input text
                else: # TEXT
                    ui.input(label, value=val, 
                             on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})
                            ).props('dense outlined').classes('w-full').props(f'id=attr-input-{t.name}')

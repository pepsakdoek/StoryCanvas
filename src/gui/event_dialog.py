import uuid
from nicegui import ui
from ..models import Event
from .dialog_utils import fill_attr_container, get_templates

def show_add_event_dialog(gui):
    form = {'name': '', 'desc': '', 'importance': gui.state.settings.importance_levels[-1], 'attributes': {}, 'x': 500, 'y': 500}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('New Event').classes('text-h6')
        ui.input('Event Name', on_change=lambda e: form.update({'name': e.value}))
        ui.textarea('Description', on_change=lambda e: form.update({'desc': e.value}))
        ui.select(gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value}))
        attr_cont = ui.column().classes('w-full gap-1')
        fill_attr_container(gui, "Event", attr_cont, form)
        ui.button('Create Event', on_click=lambda: _save_event(gui, None, form, dialog))
    dialog.open()

def show_edit_event_dialog(gui, ev: Event):
    form = {'name': ev.name, 'desc': ev.description, 'importance': ev.importance, 'attributes': ev.attributes.copy(), 'x': ev.x, 'y': ev.y}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Edit Event').classes('text-h6')
        ui.input('Name', value=form['name'], on_change=lambda e: form.update({'name': e.value}))
        ui.textarea('Description', value=form['desc'], on_change=lambda e: form.update({'desc': e.value}))
        ui.select(gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value}))
        attr_cont = ui.column().classes('w-full gap-1')
        fill_attr_container(gui, "Event", attr_cont, form)
        ui.button('Save', on_click=lambda: _save_event(gui, ev.uid, form, dialog))
    dialog.open()

def _save_event(gui, uid, form, dialog):
    if not form['name']:
        ui.notify("Name is required", type='negative')
        return

    # Validate required attributes
    templates = get_templates(gui, "Event")
    for t in templates:
        if t.required and not form['attributes'].get(t.name):
            ui.notify(f"'{t.name}' is required", type='negative')
            return

    ev = Event(uid=uid or str(uuid.uuid4()), name=form['name'], description=form['desc'], 
               importance=form['importance'], attributes=form['attributes'], x=form['x'], y=form['y'])
    gui.state.save_event(ev)
    gui._refresh_canvas_content()
    dialog.close()

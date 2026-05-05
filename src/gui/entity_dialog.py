from nicegui import ui
from .dialog_utils import fill_attr_container, get_templates

def show_add_entity_dialog(gui, etype: str):
    form = {'name': '', 'importance': gui.state.settings.importance_levels[-1], 'attributes': {}}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label(f'Add {etype}').classes('text-h6')
        ui.input('Name', on_change=lambda e: form.update({'name': e.value})).classes('w-full').props('id=entity-add-name')
        ui.select(gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value})).classes('w-full').props('id=entity-add-importance')
        attr_cont = ui.column().classes('w-full gap-1')
        fill_attr_container(gui, etype, attr_cont, form)
        ui.button('Create', on_click=lambda: _create_entity(gui, etype, form, dialog)).classes('w-full mt-4')
    dialog.open()

def _create_entity(gui, etype, form, dialog):
    import logging
    name = form['name'].strip()
    logging.info(f"Attempting to create {etype}: '{name}'")
    if not name: 
        ui.notify("Name is required", type='negative')
        return
    
    # Validate required attributes
    templates = get_templates(gui, etype)
    for t in templates:
        if t.required and not form['attributes'].get(t.name):
            ui.notify(f"'{t.name}' is required", type='negative')
            return

    uid = gui.state.create_entity(name, etype, form.get('importance', 'extra'), form['attributes'])
    logging.info(f"Entity created with UID: {uid}. Refreshing canvas...")
    gui._refresh_canvas_content()
    dialog.close()
    ui.notify(f"Created {etype}: {name}")

def show_edit_entity_dialog(gui, identity, state):
    form = {'name': identity.name, 'importance': identity.importance, 'attributes': state.attributes.copy(), 'x': state.x, 'y': state.y}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label(f'Edit {identity.name}').classes('text-h6')
        ui.input('Global Name', value=form['name'], on_change=lambda e: form.update({'name': e.value})).classes('w-full').props('id=entity-edit-name')
        ui.select(gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value})).classes('w-full').props('id=entity-edit-importance')
        with ui.row().classes('w-full gap-2'):
            ui.number('X', value=form['x'], on_change=lambda e: form.update({'x': e.value})).classes('flex-grow')
            ui.number('Y', value=form['y'], on_change=lambda e: form.update({'y': e.value})).classes('flex-grow')
        attr_cont = ui.column().classes('w-full gap-1')
        fill_attr_container(gui, identity.entity_type, attr_cont, form)
        ui.button('Save Globally', on_click=lambda: _save_entity_edit(gui, identity.uid, form, dialog)).classes('w-full mt-4')
    dialog.open()

def _save_entity_edit(gui, uid, form, dialog):
    name = form['name'].strip()
    identity = gui.state.registry.entities.get(uid)
    if identity:
        # Validate required attributes
        templates = get_templates(gui, identity.entity_type)
        for t in templates:
            if t.required and not form['attributes'].get(t.name):
                ui.notify(f"'{t.name}' is required", type='negative')
                return

    gui.state.update_identity(uid, name, form.get('importance', 'extra'))
    gui.state.update_state(uid, float(form['x']), float(form['y']), form['attributes'])
    gui._refresh_canvas_content()
    dialog.close()
    ui.notify(f"Updated {name}")

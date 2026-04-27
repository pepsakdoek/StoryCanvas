from nicegui import ui
from ..models import Relationship, RelationshipType

def show_add_relationship_dialog(gui):
    if not gui.state: return
    entities = {uid: gui.state.registry.entities[uid].name 
                for uid in gui.state.entity_states 
                if uid in gui.state.registry.entities}
    for ev in gui.state.events: entities[ev.uid] = f"[E] {ev.name}"
    
    if len(entities) < 2:
        ui.notify('Need at least 2 entities to create a relationship', type='warning')
        return

    uids = list(entities.keys())
    form = {'source': uids[0], 'target': uids[1], 'type': RelationshipType.SENTIMENT, 'desc': ''}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Add Relationship').classes('text-h6')
        ui.select(entities, label='Source').bind_value(form, 'source').classes('w-full')
        ui.select(entities, label='Target').bind_value(form, 'target').classes('w-full')
        ui.select([t.value for t in RelationshipType], label='Type').bind_value(form, 'type').classes('w-full')
        ui.input('Description').bind_value(form, 'desc').classes('w-full')
        ui.button('Create', on_click=lambda: _create_relationship(gui, form, dialog)).classes('w-full')
    dialog.open()

def _create_relationship(gui, form, dialog):
    rel = Relationship(source_uid=form['source'], target_uid=form['target'], rel_type=form['type'], description=form['desc'])
    gui.state.save_relationship(rel)
    gui._refresh_canvas_content()
    dialog.close()

def show_edit_relationship_dialog(gui, rel: Relationship):
    entities = {uid: gui.state.registry.entities[uid].name for uid in gui.state.entity_states if uid in gui.state.registry.entities}
    for ev in gui.state.events: entities[ev.uid] = f"[E] {ev.name}"
    form = {'source': rel.source_uid, 'target': rel.target_uid, 'type': rel.rel_type, 'desc': rel.description}
    with ui.dialog() as dialog, ui.card().classes('w-96'):
        ui.label('Edit Relationship').classes('text-h6')
        ui.select(entities, label='Source').bind_value(form, 'source').classes('w-full')
        ui.select(entities, label='Target').bind_value(form, 'target').classes('w-full')
        ui.select([t.value for t in RelationshipType], label='Type').bind_value(form, 'type').classes('w-full')
        ui.input('Description').bind_value(form, 'desc').classes('w-full')
        ui.button('Update', on_click=lambda: _update_relationship(gui, rel.uid, form, dialog)).classes('w-full')
    dialog.open()

def _update_relationship(gui, uid, form, dialog):
    for r in gui.state.relationships:
        if r.uid == uid:
            r.source_uid, r.target_uid, r.rel_type, r.description = form['source'], form['target'], form['type'], form['desc']
            break
    gui.state.save_relationships()
    gui._refresh_canvas_content()
    dialog.close()

import uuid
import json
from nicegui import ui
from ..models import EntityIdentity, EntityState, Event, Relationship, RelationshipType

class DialogManager:
    def __init__(self, gui):
        self.gui = gui

    def add_entity_dialog(self, etype: str):
        form = {'name': '', 'importance': self.gui.state.settings.importance_levels[-1], 'attributes': {}}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Add {etype}').classes('text-h6')
            ui.input('Name', on_change=lambda e: form.update({'name': e.value}))
            if etype == "Actor":
                ui.select(self.gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value}))
            attr_cont = ui.column().classes('w-full gap-1')
            self._fill_attr_container(etype, attr_cont, form)
            ui.button('Create', on_click=lambda: self._create_entity(etype, form, dialog))
        dialog.open()

    def _create_entity(self, etype, form, dialog):
        if not form['name']: return
        self.gui.state.create_entity(form['name'], etype, form.get('importance', 'extra'), form['attributes'])
        self.gui._refresh_canvas_content(); dialog.close()

    def edit_entity_dialog(self, identity: EntityIdentity, state: EntityState):
        form = {'name': identity.name, 'importance': identity.importance, 'attributes': state.attributes.copy(), 'x': state.x, 'y': state.y}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Edit {identity.name}').classes('text-h6')
            ui.input('Global Name', value=form['name'], on_change=lambda e: form.update({'name': e.value}))
            if identity.entity_type == "Actor":
                ui.select(self.gui.state.settings.importance_levels, label='Importance', value=form['importance'], on_change=lambda e: form.update({'importance': e.value}))
            with ui.row().classes('w-full gap-2'):
                ui.number('X', value=form['x'], on_change=lambda e: form.update({'x': e.value})).classes('flex-grow')
                ui.number('Y', value=form['y'], on_change=lambda e: form.update({'y': e.value})).classes('flex-grow')
            attr_cont = ui.column().classes('w-full gap-1')
            self._fill_attr_container(identity.entity_type, attr_cont, form)
            ui.button('Save Globally', on_click=lambda: self._save_entity_edit(identity.uid, form, dialog))
        dialog.open()

    def _save_entity_edit(self, uid, form, dialog):
        self.gui.state.update_identity(uid, form['name'], form.get('importance', 'extra'))
        self.gui.state.update_state(uid, float(form['x']), float(form['y']), form['attributes'])
        self.gui._refresh_canvas_content(); dialog.close()

    def add_event_dialog(self):
        form = {'name': '', 'desc': '', 'x': 500, 'y': 500}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('New Event').classes('text-h6')
            ui.input('Event Name', on_change=lambda e: form.update({'name': e.value}))
            ui.textarea('Description', on_change=lambda e: form.update({'desc': e.value}))
            ui.button('Create Event', on_click=lambda: self._save_event(None, form, dialog))
        dialog.open()

    def edit_event_dialog(self, ev: Event):
        form = {'name': ev.name, 'desc': ev.description, 'x': ev.x, 'y': ev.y}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Edit Event').classes('text-h6')
            ui.input('Name', value=form['name'], on_change=lambda e: form.update({'name': e.value}))
            ui.textarea('Description', value=form['desc'], on_change=lambda e: form.update({'desc': e.value}))
            ui.button('Save', on_click=lambda: self._save_event(ev.uid, form, dialog))
        dialog.open()

    def _save_event(self, uid, form, dialog):
        ev = Event(uid=uid or str(uuid.uuid4()), name=form['name'], description=form['desc'], x=form['x'], y=form['y'])
        self.gui.state.save_event(ev); self.gui._refresh_canvas_content(); dialog.close()

    def add_relationship_dialog(self):
        if not self.gui.state: return
        entities = {uid: self.gui.state.registry.entities[uid].name 
                    for uid in self.gui.state.entity_states 
                    if uid in self.gui.state.registry.entities}
        for ev in self.gui.state.events: entities[ev.uid] = f"[E] {ev.name}"
        
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
            ui.button('Create', on_click=lambda: self._create_relationship(form, dialog)).classes('w-full')
        dialog.open()

    def _create_relationship(self, form, dialog):
        rel = Relationship(source_uid=form['source'], target_uid=form['target'], rel_type=form['type'], description=form['desc'])
        self.gui.state.save_relationship(rel); self.gui._refresh_canvas_content(); dialog.close()

    def edit_relationship_dialog(self, rel: Relationship):
        entities = {uid: self.gui.state.registry.entities[uid].name for uid in self.gui.state.entity_states if uid in self.gui.state.registry.entities}
        for ev in self.gui.state.events: entities[ev.uid] = f"[E] {ev.name}"
        form = {'source': rel.source_uid, 'target': rel.target_uid, 'type': rel.rel_type, 'desc': rel.description}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Edit Relationship').classes('text-h6')
            ui.select(entities, label='Source').bind_value(form, 'source').classes('w-full')
            ui.select(entities, label='Target').bind_value(form, 'target').classes('w-full')
            ui.select([t.value for t in RelationshipType], label='Type').bind_value(form, 'type').classes('w-full')
            ui.input('Description').bind_value(form, 'desc').classes('w-full')
            ui.button('Update', on_click=lambda: self._update_relationship(rel.uid, form, dialog)).classes('w-full')
        dialog.open()

    def _update_relationship(self, uid, form, dialog):
        for r in self.gui.state.relationships:
            if r.uid == uid:
                r.source_uid, r.target_uid, r.rel_type, r.description = form['source'], form['target'], form['type'], form['desc']
                break
        self.gui.state.save_relationships(); self.gui._refresh_canvas_content(); dialog.close()

    def _fill_attr_container(self, etype, container, form):
        mapping = {"Actor": self.gui.state.settings.actor_attributes, "Place": self.gui.state.settings.place_attributes, 
                   "Item": self.gui.state.settings.item_attributes, "Knowledge": self.gui.state.settings.knowledge_attributes}
        templates = mapping.get(etype, [])
        with container:
            for t in templates:
                if t.enabled:
                    val = form['attributes'].get(t.name, '')
                    ui.input(t.name, value=val, on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})).props('dense outlined')

    def add_slot_dialog(self):
        default_name = f"Chapter {len(self.gui.state.get_slots())+1}"
        with ui.dialog() as dialog, ui.card():
            ui.label('New Chapter').classes('text-h6')
            name = ui.input('Name', placeholder=default_name)
            clone = ui.checkbox('Clone state', value=True)
            ui.button('Create', on_click=lambda: self._create_slot(name.value or default_name, clone.value, dialog))
        dialog.open()

    def _create_slot(self, name, clone, dialog):
        if self.gui.state.create_slot(name, clone): dialog.close(); self.gui.build_canvas()

    def edit_settings_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            ui.label('Settings').classes('text-h6 mb-4')
            with ui.tabs() as tabs: ui.tab('General'); ui.tab('Actors'); ui.tab('Places')
            with ui.tab_panels(tabs, value='General').classes('w-full'):
                with ui.tab_panel('General'):
                    ui.label('Importance Levels').classes('text-caption font-bold text-slate-500 mb-2')
                    for i, level in enumerate(self.gui.state.settings.importance_levels):
                        with ui.row().classes('w-full items-center'):
                            ui.input(value=level, on_change=lambda e, idx=i: self._update_imp_name(idx, e.value)).props('dense outlined').classes('flex-grow')
                    ui.button('Add Level', on_click=lambda: self._add_imp_level(dialog)).props('flat icon=add').classes('mb-4')
                    
                    ui.separator().classes('my-4')
                    ui.label('Grid Settings').classes('text-caption font-bold text-slate-500 mb-2')
                    ui.checkbox('Snap to Grid', value=self.gui.state.settings.snap_to_grid, 
                                on_change=lambda e: setattr(self.gui.state.settings, 'snap_to_grid', e.value))
                    ui.number('Grid Size', value=self.gui.state.settings.grid_size, suffix='px',
                              on_change=lambda e: setattr(self.gui.state.settings, 'grid_size', int(e.value)))
            ui.button('Save', on_click=lambda: self._save_settings(dialog))
        dialog.open()

    def _update_imp_name(self, idx, val): self.gui.state.settings.importance_levels[idx] = val
    def _add_imp_level(self, dialog): self.gui.state.settings.importance_levels.append("new level"); dialog.close(); self.edit_settings_dialog()
    def _save_settings(self, dialog): self.gui.state.save_settings(self.gui.state.settings); dialog.close()

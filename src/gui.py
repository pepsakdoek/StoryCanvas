import os
import shutil
import uuid
import math
from typing import Optional, Dict, List, Type, Any
from nicegui import ui, events
from .storage import CanvasState, get_available_canvases, SAVES_DIR
from .models import EntityIdentity, EntityState, Event, Relationship, DefaultImportance, RelationshipType, AttributeTemplate, CanvasSettings

class StoryCanvasGUI:
    def __init__(self):
        self.state: Optional[CanvasState] = None
        self.active_entity: Optional[Dict[str, Any]] = None
        self.canvas_container: Optional[ui.element] = None
        self._setup_styles()
        self.container = ui.element('div').classes('w-full h-full')
        self.importance_filter = {} 
        self.type_filter = {
            'Actor': True,
            'Place': True,
            'Item': True,
            'Knowledge': True,
            'Event': True
        }

    def _setup_styles(self):
        ui.add_head_html('''
            <style>
                .canvas-container {
                    width: 100vw; height: 100vh;
                    background-color: #f0f4f8;
                    position: relative; overflow: hidden;
                }
                .grid-overlay {
                    position: absolute; top: 0; left: 0;
                    width: 10000px; height: 10000px;
                    background-image: 
                        linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
                    background-size: 50px 50px;
                    pointer-events: none; z-index: 0;
                }
                .entity-block {
                    width: 120px; min-height: 80px;
                    background-color: #ffffff;
                    border: 2px solid #94a3b8;
                    border-radius: 12px;
                    display: flex; flex-direction: column;
                    align-items: center; justify-content: center;
                    text-align: center; position: absolute;
                    cursor: move; z-index: 10;
                    font-size: 0.85rem; padding: 8px;
                    user-select: none;
                    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                    transition: transform 0.15s, box-shadow 0.15s;
                }
                .entity-block:hover {
                    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
                    transform: translateY(-2px);
                }
                .entity-actor { border-left: 6px solid #ef4444; }
                .entity-place { border-left: 6px solid #22c55e; }
                .entity-item { border-left: 6px solid #eab308; }
                .entity-knowledge { border-left: 6px solid #a855f7; }
                .entity-event { border: 2px dashed #64748b; border-radius: 50%; width: 100px; height: 100px; background-color: #f1f5f9; }
                
                .relationship-line {
                    position: absolute; height: 2px;
                    background-color: #94a3b8;
                    transform-origin: top left;
                    pointer-events: none; z-index: 5;
                    opacity: 0.6;
                }
                /* Arrowhead for the line */
                .relationship-line::after {
                    content: '';
                    position: absolute;
                    right: 0;
                    top: -4px;
                    border-top: 5px solid transparent;
                    border-bottom: 5px solid transparent;
                    border-left: 8px solid #94a3b8;
                }
                .relationship-label {
                    position: absolute;
                    font-size: 10px;
                    font-weight: bold;
                    background-color: rgba(255, 255, 255, 0.9);
                    padding: 2px 6px;
                    border-radius: 10px;
                    border: 1px solid #cbd5e1;
                    color: #475569;
                    pointer-events: none;
                    z-index: 6;
                    white-space: nowrap;
                    transform: translate(-50%, -50%);
                }
                
                .timeline-bar {
                    position: absolute; bottom: 20px; left: 50%;
                    transform: translateX(-50%); z-index: 100;
                    background-color: rgba(255, 255, 255, 0.9);
                    backdrop-filter: blur(8px);
                    padding: 10px 20px; border-radius: 50px;
                    box-shadow: 0 10px 25px -5px rgba(0,0,0,0.1);
                    border: 1px solid rgba(0,0,0,0.05);
                    display: flex; align-items: center; gap: 15px;
                }
                .slot-bubble {
                    width: 12px; height: 12px; border-radius: 50%;
                    background-color: #cbd5e1; cursor: pointer;
                    transition: transform 0.2s, background-color 0.2s;
                }
                .slot-bubble.active { background-color: #3b82f6; transform: scale(1.4); }
            </style>
        ''')

    def _handle_mousedown(self, e: events.MouseEventArguments, card, uid, is_event):
        if is_event:
            ev = next((ev for ev in self.state.events if ev.uid == uid), None)
            start_x, start_y = ev.x, ev.y
        else:
            state = self.state.entity_states.get(uid)
            start_x, start_y = state.x, state.y

        # GenericEventArguments store JS properties in the 'args' dict
        self.active_entity = {
            'card': card,
            'uid': uid,
            'is_event': is_event,
            'start_mouse_x': e.args['clientX'],
            'start_mouse_y': e.args['clientY'],
            'start_obj_x': start_x,
            'start_obj_y': start_y,
            'current_x': start_x,
            'current_y': start_y
        }
        card.classes(add='z-50 shadow-2xl scale-105')

    def _handle_mousemove(self, e: events.MouseEventArguments):
        if not self.active_entity:
            return
        
        dx = e.args['clientX'] - self.active_entity['start_mouse_x']
        dy = e.args['clientY'] - self.active_entity['start_mouse_y']
        
        self.active_entity['current_x'] = self.active_entity['start_obj_x'] + dx
        self.active_entity['current_y'] = self.active_entity['start_obj_y'] + dy
        
        self.active_entity['card'].style(
            f"left: {self.active_entity['current_x']}px; "
            f"top: {self.active_entity['current_y']}px; "
            f"transition: none;"
        )

    def _handle_mouseup(self):
        if not self.active_entity:
            return
            
        data = {
            'uid': self.active_entity['uid'],
            'x': self.active_entity['current_x'],
            'y': self.active_entity['current_y'],
            'isEvent': self.active_entity['is_event']
        }
        
        # Reset card visual state
        self.active_entity['card'].classes(remove='z-50 shadow-2xl scale-105')
        
        # Persist the change
        self._handle_pos_update(data)
        
        self.active_entity = None

    def _handle_pos_update(self, data):
        if not self.state: return
        uid, x, y, is_ev = data['uid'], data['x'], data['y'], data.get('isEvent', False)
        if is_ev:
            for ev in self.state.events:
                if ev.uid == uid:
                    ev.x, ev.y = float(x), float(y)
                    self.state.save_event(ev)
                    break
        else:
            self.state.update_state(uid, float(x), float(y), self.state.entity_states[uid].attributes)
        self._refresh_canvas_content()

    def build_selector(self):
        self.container.clear()
        with self.container:
            with ui.card().classes('absolute-center w-96 p-8 shadow-2xl'):
                ui.label('StoryCanvas').classes('text-h4 mb-2 text-center w-full font-bold text-blue-600')
                canvases = get_available_canvases()
                with ui.column().classes('w-full gap-3'):
                    for name in canvases:
                        ui.button(name, on_click=lambda n=name: self.load_canvas(n)).classes('w-full')
                    ui.separator().classes('my-4')
                    new_name = ui.input('New Canvas Name').classes('w-full')
                    ui.button('Create', on_click=lambda: self.load_canvas(new_name.value)).classes('w-full')

    def load_canvas(self, name: str):
        if not name: return
        self.state = CanvasState(name.strip())
        self.importance_filter = {level: True for level in self.state.settings.importance_levels}
        self.build_canvas()

    def build_canvas(self):
        self.container.clear()
        with self.container:
            with ui.row().classes('absolute top-4 left-4 z-50 bg-white/90 backdrop-blur p-3 rounded-xl shadow border gap-4'):
                for etype in ['Actor', 'Place', 'Item', 'Knowledge', 'Event']:
                    ui.checkbox(etype, value=self.type_filter.get(etype, True), 
                               on_change=lambda e, t=etype: self._toggle_type_filter(t, e.value))
                ui.separator().props('vertical')
                ui.button(icon='person_add', on_click=lambda: self.add_entity_dialog("Actor")).props('round unelevated color=red-5').tooltip("Add Actor")
                ui.button(icon='add_location', on_click=lambda: self.add_entity_dialog("Place")).props('round unelevated color=green-5').tooltip("Add Place")
                ui.button(icon='category', on_click=lambda: self.add_entity_dialog("Item")).props('round unelevated color=yellow-7').tooltip("Add Item")
                ui.button(icon='menu_book', on_click=lambda: self.add_entity_dialog("Knowledge")).props('round unelevated color=purple-5').tooltip("Add Knowledge")
                ui.button(icon='bolt', on_click=self.add_event_dialog).props('round unelevated color=slate-600').tooltip("Add Event")
                ui.button(icon='link', on_click=self.add_relationship_dialog).props('round unelevated color=purple').tooltip("Add Relationship")
                ui.button(icon='settings', on_click=self.edit_settings_dialog).props('round flat color=slate-600')
                ui.button(icon='home', on_click=self.build_selector).props('round flat color=slate-600')

            self.canvas_container = ui.element('div').classes('canvas-container')
            self.canvas_container.on('mousemove', self._handle_mousemove)
            self.canvas_container.on('mouseup', self._handle_mouseup)
            self.canvas_container.on('mouseleave', self._handle_mouseup)
            
            with self.canvas_container:
                self._refresh_canvas_content()
            self._build_timeline_bar()

    def _toggle_type_filter(self, etype, value):
        self.type_filter[etype] = value
        self._refresh_canvas_content()

    def _refresh_canvas_content(self):
        self.canvas_container.clear()
        with self.canvas_container:
            ui.element('div').classes('grid-overlay')
            self._draw_relationships()
            
            # Entities
            for uid, state in self.state.entity_states.items():
                identity = self.state.registry.entities.get(uid)
                if not identity: continue
                if not self.type_filter.get(identity.entity_type, True): continue
                if identity.entity_type == 'Actor' and not self.importance_filter.get(identity.importance, True): continue
                
                css = f"entity-{identity.entity_type.lower()}"
                self._add_entity_to_ui(identity, state, css)
            
            # Events
            if self.type_filter.get('Event', True):
                for ev in self.state.events:
                    self._add_event_to_ui(ev)

    def _add_entity_to_ui(self, identity: EntityIdentity, state: EntityState, css_class: str):
        with self.canvas_container:
            card = ui.card().classes(f'entity-block p-0 {css_class}') \
                .style(f'left: {state.x}px; top: {state.y}px')
            with card:
                ui.label(identity.name).classes('font-bold mt-1')
                if identity.entity_type == 'Actor':
                    ui.label(identity.importance).classes('text-[10px] uppercase text-slate-400')
                with ui.context_menu():
                    ui.menu_item('Edit', on_click=lambda: self.edit_entity_dialog(identity, state))
                    ui.menu_item('Delete from Slot', on_click=lambda: self._delete_entity(identity.uid))
            card.on('mousedown', lambda e: self._handle_mousedown(e, card, identity.uid, False))
            card.on('dblclick', lambda: self.edit_entity_dialog(identity, state))

    def _add_event_to_ui(self, ev: Event):
        with self.canvas_container:
            card = ui.card().classes('entity-block entity-event p-2') \
                .style(f'left: {ev.x}px; top: {ev.y}px')
            with card:
                ui.label(ev.name).classes('font-bold text-center')
                ui.icon('bolt').classes('text-slate-400')
                with ui.context_menu():
                    ui.menu_item('Edit Event', on_click=lambda: self.edit_event_dialog(ev))
                    ui.menu_item('Delete Event', on_click=lambda: self._delete_event(ev.uid))
            card.on('mousedown', lambda e: self._handle_mousedown(e, card, ev.uid, True))
            card.on('dblclick', lambda: self.edit_event_dialog(ev))

    def edit_entity_dialog(self, identity: EntityIdentity, state: EntityState):
        form = {
            'name': identity.name,
            'importance': identity.importance,
            'attributes': state.attributes.copy(),
            'x': state.x, 'y': state.y
        }
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Edit {identity.name}').classes('text-h6')
            ui.input('Global Name', value=form['name'], on_change=lambda e: form.update({'name': e.value}))
            if identity.entity_type == "Actor":
                ui.select(self.state.settings.importance_levels, label='Importance', value=form['importance'],
                          on_change=lambda e: form.update({'importance': e.value}))
            
            with ui.row().classes('w-full gap-2'):
                ui.number('X', value=form['x'], on_change=lambda e: form.update({'x': e.value})).classes('flex-grow')
                ui.number('Y', value=form['y'], on_change=lambda e: form.update({'y': e.value})).classes('flex-grow')
            
            attr_cont = ui.column().classes('w-full gap-1')
            self._fill_attr_container(identity.entity_type, attr_cont, form)
            
            ui.button('Save Globally', on_click=lambda: self._save_edit(identity.uid, form, dialog))
        dialog.open()

    def _save_edit(self, uid, form, dialog):
        self.state.update_identity(uid, form['name'], form.get('importance', 'extra'))
        self.state.update_state(uid, float(form['x']), float(form['y']), form['attributes'])
        self._refresh_canvas_content()
        dialog.close()

    def add_entity_dialog(self, etype: str):
        form = {'name': '', 'importance': self.state.settings.importance_levels[-1], 'attributes': {}}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label(f'Add {etype}').classes('text-h6')
            ui.input('Name', on_change=lambda e: form.update({'name': e.value}))
            if etype == "Actor":
                ui.select(self.state.settings.importance_levels, label='Importance', value=form['importance'],
                          on_change=lambda e: form.update({'importance': e.value}))
            attr_cont = ui.column().classes('w-full gap-1')
            self._fill_attr_container(etype, attr_cont, form)
            ui.button('Create', on_click=lambda: self._create_entity(etype, form, dialog))
        dialog.open()

    def _create_entity(self, etype, form, dialog):
        if not form['name']: return
        self.state.create_entity(form['name'], etype, form.get('importance', 'extra'), form['attributes'])
        self._refresh_canvas_content()
        dialog.close()

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
        self.state.save_event(ev)
        self._refresh_canvas_content()
        dialog.close()

    def _fill_attr_container(self, etype, container, form):
        mapping = {"Actor": self.state.settings.actor_attributes, "Place": self.state.settings.place_attributes, 
                   "Item": self.state.settings.item_attributes, "Knowledge": self.state.settings.knowledge_attributes}
        templates = mapping.get(etype, [])
        with container:
            for t in templates:
                if t.enabled:
                    val = form['attributes'].get(t.name, '')
                    ui.input(t.name, value=val, on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})).props('dense outlined')

    def _build_timeline_bar(self):
        with ui.element('div').classes('timeline-bar'):
            ui.label('Slots:').classes('text-xs font-bold text-slate-400')
            for slot in self.state.get_slots():
                active = slot == self.state.current_slot
                ui.element('div').classes('slot-bubble' + (' active' if active else '')) \
                    .on('click', lambda _, s=slot: self._switch_slot(s)).tooltip(slot)
            ui.button(icon='add', on_click=self.add_slot_dialog).props('round flat dense color=blue')

    def _switch_slot(self, name):
        self.state.switch_slot(name)
        self.build_canvas()

    def add_slot_dialog(self):
        with ui.dialog() as dialog, ui.card():
            ui.label('New Chapter').classes('text-h6')
            name = ui.input('Name', placeholder=f"Chapter {len(self.state.get_slots())+1}")
            clone = ui.checkbox('Clone state', value=True)
            ui.button('Create', on_click=lambda: self._create_slot(name.value or name.placeholder, clone.value, dialog))
        dialog.open()

    def _create_slot(self, name, clone, dialog):
        if self.state.create_slot(name, clone):
            dialog.close(); self.build_canvas()

    def _draw_relationships(self):
        for rel in self.state.relationships:
            src_state = self.state.entity_states.get(rel.source_uid)
            dst_state = self.state.entity_states.get(rel.target_uid)
            if src_state and dst_state:
                # Center point of source card (120x80)
                x1, y1 = src_state.x + 60, src_state.y + 40
                # Center point of target card
                x2, y2 = dst_state.x + 60, dst_state.y + 40
                
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx*dx + dy*dy)
                if dist == 0: continue
                
                angle = math.atan2(dy, dx) * 180 / math.pi
                
                # Draw the line
                ui.element('div').classes('relationship-line').style(
                    f'left: {x1}px; top: {y1}px; width: {dist}px; transform: rotate({angle}deg)'
                )
                
                # Draw the description label at the midpoint
                mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2
                with ui.element('div').classes('relationship-label').style(f'left: {mid_x}px; top: {mid_y}px'):
                    ui.label(rel.description)

    def _delete_entity(self, uid):
        self.state.delete_entity(uid); self._refresh_canvas_content()

    def _delete_event(self, uid):
        self.state.events = [e for e in self.state.events if e.uid != uid]
        # Manually persist
        with open(self.state.events_file, "w") as f:
            import json
            json.dump([e.model_dump() for e in self.state.events], f, indent=4)
        self._refresh_canvas_content()

    def add_relationship_dialog(self):
        if not self.state: return
        entities = {uid: self.state.registry.entities[uid].name 
                    for uid in self.state.entity_states 
                    if uid in self.state.registry.entities}
        
        if len(entities) < 2:
            ui.notify('Need at least 2 entities to create a relationship', type='warning')
            return

        uids = list(entities.keys())
        form = {
            'source': uids[0],
            'target': uids[1],
            'type': RelationshipType.SENTIMENT,
            'desc': ''
        }

        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Relationship').classes('text-h6')
            ui.select(entities, label='Source').bind_value(form, 'source').classes('w-full')
            ui.select(entities, label='Target').bind_value(form, 'target').classes('w-full')
            ui.select([t.value for t in RelationshipType], label='Type').bind_value(form, 'type').classes('w-full')
            ui.input('Description').bind_value(form, 'desc').classes('w-full')
            
            ui.button('Create', on_click=lambda: self._create_relationship(form, dialog)).classes('w-full')
        dialog.open()

    def _create_relationship(self, form, dialog):
        rel = Relationship(
            source_uid=form['source'],
            target_uid=form['target'],
            rel_type=form['type'],
            description=form['desc']
        )
        self.state.save_relationship(rel)
        self._refresh_canvas_content()
        dialog.close()

    def edit_settings_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            ui.label('Settings').classes('text-h6 mb-4')
            with ui.tabs() as tabs:
                ui.tab('General'); ui.tab('Actors'); ui.tab('Places')
            with ui.tab_panels(tabs, value='General').classes('w-full'):
                with ui.tab_panel('General'):
                    for i, level in enumerate(self.state.settings.importance_levels):
                        with ui.row().classes('w-full items-center'):
                            ui.input(value=level, on_change=lambda e, idx=i: self._update_imp_name(idx, e.value)).props('dense outlined').classes('flex-grow')
                    ui.button('Add Level', on_click=lambda: self._add_imp_level(dialog)).props('flat icon=add')
            ui.button('Save', on_click=lambda: self._save_settings(dialog))
        dialog.open()

    def _update_imp_name(self, idx, val): self.state.settings.importance_levels[idx] = val
    def _add_imp_level(self, dialog): self.state.settings.importance_levels.append("new level"); dialog.close(); self.edit_settings_dialog()
    def _save_settings(self, dialog): self.state.save_settings(self.state.settings); dialog.close()

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=False, reload=False)

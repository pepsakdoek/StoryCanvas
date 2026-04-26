import os
import shutil
import uuid
from typing import Optional, Dict, List, Type, Any
from nicegui import app, ui, events
from ..storage import CanvasState, get_available_canvases, SAVES_DIR
from ..models import EntityIdentity, EntityState, Event, Relationship, DefaultImportance, RelationshipType, AttributeTemplate, CanvasSettings
from .styles import setup_styles
from .dialogs import DialogManager
from .canvas_manager import CanvasManager

class StoryCanvasGUI:
    def __init__(self):
        self.state: Optional[CanvasState] = None
        self.active_entity: Optional[Dict[str, Any]] = None
        self.canvas_container: Optional[ui.element] = None
        
        # Panning state
        self.is_panning_mode = False
        self.is_panning = False
        self.pan_offset = {'x': 0, 'y': 0}
        self.last_mouse = {'x': 0, 'y': 0}
        
        # Managers
        self.dialogs = DialogManager(self)
        self.canvas = CanvasManager(self)
        
        setup_styles()
        self.container = ui.element('div').classes('w-full h-full')
        
        # Filters
        self.importance_filter = {} 
        self.type_filter = {'Actor': True, 'Place': True, 'Item': True, 'Knowledge': True, 'Event': True}

    def build_selector(self):
        self.container.clear()
        with self.container:
            with ui.card().classes('absolute-center w-96 p-8 shadow-2xl'):
                ui.label('Story Canvas').classes('text-h4 mb-2 text-center w-full font-bold text-blue-600')
                ui.label('Story creation and narrative visualisation assistance').classes('text-h5 mb-2 text-center w-full font-bold text-blue-700')
                canvases = get_available_canvases()
                with ui.column().classes('w-full gap-3'):
                    for name in canvases:
                        ui.button(name, on_click=lambda n=name: self.load_canvas(n)).classes('w-full')
                    ui.separator().classes('my-4')
                    new_name = ui.input('New Canvas Name').classes('w-full')
                    ui.button('Create', on_click=lambda: self.load_canvas(new_name.value)).classes('w-full')
                    ui.separator().classes('my-2')
                    with ui.row().classes('w-full gap-2'):
                        ui.button('Help', on_click=self.show_help).classes('grow').props('outline color=blue')
                        ui.button('Exit', on_click=app.shutdown).classes('grow').props('outline color=red')

    def show_help(self):
        try:
            with open('documentation/usage.md', 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            content = "Usage guide not found."
        
        with ui.dialog() as dialog, ui.card().classes('w-[600px] max-w-full'):
            ui.markdown(content)
            ui.button('Close', on_click=dialog.close).classes('w-full mt-4')
        dialog.open()

    def load_canvas(self, name: str):
        if not name: return
        self.state = CanvasState(name.strip())
        self.importance_filter = {level: True for level in self.state.settings.importance_levels}
        self.build_canvas()

    def build_canvas(self):
        self.container.clear()
        with self.container:
            # HEADER BAR
            with ui.element('div').classes('header-bar'):
                with ui.row().classes('items-center gap-4'):
                    ui.button(icon='home', on_click=self.build_selector).props('flat round color=slate-600')
                    ui.separator().props('vertical')
                    for etype in ['Actor', 'Place', 'Item', 'Knowledge', 'Event']:
                        ui.checkbox(etype, value=self.type_filter.get(etype, True), 
                                   on_change=lambda e, t=etype: self._toggle_type_filter(t, e.value)).classes('text-xs')
                    ui.separator().props('vertical')
                    ui.button(icon='person_add', on_click=lambda: self.dialogs.add_entity_dialog("Actor")).props('round unelevated dense color=red-5')
                    ui.button(icon='add_location', on_click=lambda: self.dialogs.add_entity_dialog("Place")).props('round unelevated dense color=green-5')
                    ui.button(icon='category', on_click=lambda: self.dialogs.add_entity_dialog("Item")).props('round unelevated dense color=yellow-7')
                    ui.button(icon='menu_book', on_click=lambda: self.dialogs.add_entity_dialog("Knowledge")).props('round unelevated dense color=purple-5')
                    ui.button(icon='bolt', on_click=self.dialogs.add_event_dialog).props('round unelevated dense color=slate-600')
                    ui.button(icon='link', on_click=self.dialogs.add_relationship_dialog).props('round unelevated dense color=blue-5')
                    ui.button(icon='auto_awesome', on_click=self._auto_arrange).props('round unelevated dense color=amber-5').tooltip("Auto-Arrange")

                with ui.row().classes('items-center gap-2'):
                    ui.label('Chapters:').classes('text-[10px] font-bold text-slate-400 uppercase tracking-wider')
                    for i, slot in enumerate(self.state.get_slots()):
                        active = slot == self.state.current_slot
                        with ui.element('div').classes('slot-bubble' + (' active' if active else '')) \
                            .on('click', lambda _, s=slot: self._switch_slot(s)).tooltip(slot):
                            ui.label(str(i+1))
                    ui.button(icon='add', on_click=self.dialogs.add_slot_dialog).props('round flat dense color=blue')
                    ui.separator().props('vertical')
                    ui.button(icon='settings', on_click=self.dialogs.edit_settings_dialog).props('round flat color=slate-400')

            self.canvas_container = ui.element('div').classes('canvas-container')
            self.canvas_container.on('mousedown', self._handle_canvas_mousedown)
            self.canvas_container.on('mousemove', self._handle_mousemove)
            self.canvas_container.on('mouseup', self._handle_mouseup)
            self.canvas_container.on('mouseleave', self._handle_mouseup)
            
            # Key listeners for panning
            ui.keyboard_listener(on_key=self._handle_key)

            with self.canvas_container:
                self.canvas.refresh_canvas_content()

    def _handle_key(self, e: events.KeyEventArguments):
        if e.key == ' ':
            self.is_panning_mode = e.action.keydown
            if self.is_panning_mode:
                self.canvas_container.classes(add='cursor-grab')
            else:
                self.canvas_container.classes(remove='cursor-grab cursor-grabbing')
                self.is_panning = False

    def _handle_canvas_mousedown(self, e: events.MouseEventArguments):
        if self.is_panning_mode:
            self.is_panning = True
            self.last_mouse = {'x': e.args['clientX'], 'y': e.args['clientY']}
            self.canvas_container.classes(add='cursor-grabbing')

    def _toggle_type_filter(self, etype, value):
        self.type_filter[etype] = value; self._refresh_canvas_content()

    def _refresh_canvas_content(self):
        self.canvas.refresh_canvas_content()

    def _switch_slot(self, name):
        self.state.switch_slot(name); self.build_canvas()

    def _delete_entity(self, uid):
        self.state.delete_entity(uid); self._refresh_canvas_content()

    def _delete_event(self, uid):
        self.state.events = [e for e in self.state.events if e.uid != uid]
        with open(self.state.events_file, "w") as f:
            import json
            json.dump([e.model_dump() for e in self.state.events], f, indent=4)
        self._refresh_canvas_content()

    def _delete_relationship(self, uid):
        self.state.relationships = [r for r in self.state.relationships if r.uid != uid]
        self.state.save_relationships(); self._refresh_canvas_content()

    def _auto_arrange(self):
        if self.state:
            self.state.auto_arrange()
            self._refresh_canvas_content()
            ui.notify("Canvas auto-arranged!")

    # Drag & Drop Handlers
    def _handle_mousedown(self, e: events.MouseEventArguments, card, uid, is_event):
        # Ignore right-clicks (button 2) to allow context menu without starting a drag/refresh
        if e.args.get('button') == 2:
            return

        if is_event:
            ev = next((ev for ev in self.state.events if ev.uid == uid), None)
            sx, sy = ev.x, ev.y
        else:
            state = self.state.entity_states.get(uid)
            sx, sy = state.x, state.y

        self.active_entity = {'card': card, 'uid': uid, 'is_event': is_event, 'smx': e.args['clientX'], 'smy': e.args['clientY'], 'sox': sx, 'soy': sy, 'cx': sx, 'cy': sy}
        card.classes(add='z-50 shadow-2xl scale-105')

    def _handle_mousemove(self, e: events.MouseEventArguments):
        if not self.active_entity: return
        dx = e.args['clientX'] - self.active_entity['smx']
        dy = e.args['clientY'] - self.active_entity['smy']
        self.active_entity['cx'] = self.active_entity['sox'] + dx
        self.active_entity['cy'] = self.active_entity['soy'] + dy
        self.active_entity['card'].style(f"left: {self.active_entity['cx']}px; top: {self.active_entity['cy']}px; transition: none;")

    def _handle_mouseup(self):
        if not self.active_entity: return
        data = {'uid': self.active_entity['uid'], 'x': self.active_entity['cx'], 'y': self.active_entity['cy'], 'isEvent': self.active_entity['is_event']}
        self.active_entity['card'].classes(remove='z-50 shadow-2xl scale-105')
        self._handle_pos_update(data)
        self.active_entity = None

    def _handle_pos_update(self, data):
        if not self.state: return
        uid, x, y, is_ev = data['uid'], data['x'], data['y'], data.get('isEvent', False)
        if is_ev:
            for ev in self.state.events:
                if ev.uid == uid:
                    ev.x, ev.y = float(x), float(y)
                    self.state.save_event(ev); break
        else:
            self.state.update_state(uid, float(x), float(y), self.state.entity_states[uid].attributes)
        self._refresh_canvas_content()

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=False, reload=False)

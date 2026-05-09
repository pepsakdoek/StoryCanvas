import os
import shutil
import uuid
from typing import Optional, Dict, List, Type, Any
from nicegui import app, ui, events
from ..storage import CanvasState, get_available_canvases, SAVES_DIR
from ..models import EntityIdentity, EntityState, Event, Relationship, DefaultImportance, RelationshipType, AttributeTemplate, CanvasSettings
from .styles import setup_styles
from .dialog_manager import DialogManager
from .canvas_manager import CanvasManager

class StoryCanvasGUI:
    def __init__(self):
        import logging
        logging.info("Initializing StoryCanvasGUI...")
        self.state: Optional[CanvasState] = None
        self.active_entity: Optional[Dict[str, Any]] = None
        self.active_beat_idx = -1
        self.canvas_container: Optional[ui.element] = None
        self.canvas_content: Optional[ui.element] = None
        
        # Panning state
        self.is_panning_mode = False
        self.is_panning = False
        self.pan_offset = {'x': 0, 'y': 0}
        self.last_mouse = {'x': 0, 'y': 0}
        
        # Managers
        self.dialogs = DialogManager(self)
        self.canvas = CanvasManager(self)
        
        setup_styles()
        # Force h-screen to ensure the root container fills the viewport
        self.container = ui.element('div').classes('w-screen h-screen flex flex-col overflow-hidden').props('id=main-layout')
        
        # Filters
        self.importance_filter = {} 
        self.type_filter = {'Actor': True, 'Place': True, 'Item': True, 'Knowledge': True, 'Event': True}
        self.active_attr_tab = 'Actors'
        
        # Prose saving debounce
        self.prose_save_timer: Optional[ui.timer] = None
        
        logging.info("StoryCanvasGUI initialized.")

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
        import logging
        logging.info(f"Building canvas for {self.state.canvas_name}...")
        self.container.clear()
        with self.container:
            # HEADER BAR
            with ui.element('div').classes('header-bar'):
                with ui.row().classes('items-center gap-4'):
                    ui.button(icon='home', on_click=self.build_selector).props('flat round color=slate-600').tooltip("Home")
                    ui.separator().props('vertical')
                    # Importance Level Filters (Dynamic from story settings)
                    with ui.row().classes('items-center gap-2 bg-slate-50 p-1 px-2 rounded-lg border border-slate-200'):
                        ui.icon('filter_list', size='xs').classes('text-slate-400')
                        for level in self.state.settings.importance_levels:
                            ui.checkbox(level.title(), value=self.importance_filter.get(level, True), 
                                       on_change=lambda e, l=level: self._toggle_importance_filter(l, e.value)).classes('text-[10px] font-bold text-slate-600')
                    ui.separator().props('vertical')
                    ui.button(icon='person_add', on_click=lambda: self.dialogs.add_entity_dialog("Actor")).props('round unelevated dense color=red-5').tooltip("Add Actor")
                    ui.button(icon='add_location', on_click=lambda: self.dialogs.add_entity_dialog("Place")).props('round unelevated dense color=green-5').tooltip("Add Place")
                    ui.button(icon='category', on_click=lambda: self.dialogs.add_entity_dialog("Item")).props('round unelevated dense color=yellow-7').tooltip("Add Item")
                    ui.button(icon='menu_book', on_click=lambda: self.dialogs.add_entity_dialog("Knowledge")).props('round unelevated dense color=purple-5').tooltip("Add Knowledge")
                    ui.button(icon='bolt', on_click=self.dialogs.add_event_dialog).props('round unelevated dense color=slate-600').tooltip("Add Event")
                    ui.button(icon='link', on_click=self.dialogs.add_relationship_dialog).props('round unelevated dense color=blue-5').tooltip("Add Relationship")
                    ui.button(icon='casino', on_click=self.dialogs.open_generator_dialog).props('round unelevated dense color=orange-5').tooltip("Random Generator")
                    ui.button(icon='auto_awesome', on_click=self._auto_arrange).props('round unelevated dense color=amber-5').tooltip("Auto-Arrange")

                with ui.row().classes('items-center gap-2'):
                    ui.label('Chapters:').classes('text-[10px] font-bold text-slate-400 uppercase tracking-wider')
                    for i, slot in enumerate(self.state.get_slots()):
                        active = slot == self.state.current_slot
                        bubble = ui.element('div').classes('slot-bubble' + (' active' if active else '')) \
                            .on('click', lambda _, s=slot: self._switch_slot(s)).tooltip(slot)
                        with bubble:
                            ui.label(str(i+1))
                            with ui.menu():
                                ui.menu_item('Delete Chapter', on_click=lambda s=slot: self._delete_slot(s)).classes('text-red-500')
                    ui.button(icon='add', on_click=self.dialogs.add_slot_dialog).props('round flat dense color=blue').tooltip("Add Chapter")
                    ui.separator().props('vertical')
                    ui.button(icon='settings', on_click=self.dialogs.edit_settings_dialog).props('round flat color=slate-400').tooltip("Canvas Settings")

            # Key listeners for panning (global)
            ui.keyboard(on_key=self._handle_key)

            # Main content area: Canvas on left (75%) + Prose on right (25%)
            with ui.row().classes('w-full flex-1 gap-0 overflow-hidden').props('id=workspace-row'):
                # ... (canvas and prose panels)
                # Canvas area (75%)
                self.canvas_container = ui.element('div').classes('canvas-container w-3/4 h-full relative').props('id=canvas-viewport')
                self.canvas_container.on('mousedown', self._handle_canvas_mousedown)
                self.canvas_container.on('mousemove', self._handle_mousemove)
                self.canvas_container.on('mouseup', self._handle_mouseup)
                self.canvas_container.on('mouseleave', self._handle_mouseup)

                with self.canvas_container:
                    # Debug Placeholder
                    ui.label("CANVAS CONTAINER ACTIVE").classes('absolute-center text-slate-200 text-4xl pointer-events-none opacity-20 z-0')
                    
                    # Inner content that will be transformed for panning
                    self.canvas_content = ui.element('div').classes('canvas-content').props('id=canvas-surface')
                    self._apply_pan()
                    with self.canvas_content:
                        self.canvas.refresh_canvas_content()
                
                # Prose area (25%)
                with ui.column().classes('w-1/4 h-full border-l border-slate-300 overflow-hidden bg-white').props('id=prose-panel'):
                    self._build_prose_panel()

            # FOOTER TIMELINE BAR
            with ui.row().classes('w-full h-12 bg-slate-800 text-white items-center px-4 gap-4 z-[100] shadow-[0_-2px_10px_rgba(0,0,0,0.2)]'):
                ui.icon('reorder').classes('text-slate-400')
                
                tmap = self.state.get_timeline_map()
                
                # Find current global index
                current_idx = 0
                for i, m in enumerate(tmap['mapping']):
                    if m['slot'] == self.state.current_slot:
                        current_idx = i
                        break

                self.timeline_label = ui.label(f"Chapter: {self.state.current_slot} | Beat: 1").classes('text-[10px] font-mono w-48 text-slate-300')
                
                self.timeline_slider = ui.slider(min=0, max=tmap['total_beats'] - 1, value=current_idx, on_change=lambda e: self._on_timeline_change(e.value)) \
                    .classes('grow').props('color=blue-5 dark label-always')
                
                ui.label(f"{tmap['total_beats']} Total Beats").classes('text-[10px] font-mono text-slate-500')

    def _on_timeline_change(self, value):
        if not self.state: return
        tmap = self.state.get_timeline_map()
        if value >= len(tmap['mapping']): return
        
        info = tmap['mapping'][value]
        target_slot = info['slot']
        target_beat = info['beat_idx']
        
        self.timeline_label.text = f"Chapter: {target_slot} | Beat: {target_beat + 1}"
        self.active_beat_idx = target_beat

        if target_slot != self.state.current_slot:
            self.state.switch_slot(target_slot)
            self.build_canvas()
        
        # Precise scrolling in the rich editor using JS
        # We look for the n-th paragraph or div in the editor and scroll to it
        js_scroll = f"""
            var editor = document.getElementById('prose-editor');
            if (editor) {{
                var paras = editor.querySelectorAll('p, div');
                if (paras.length > {target_beat}) {{
                    paras[{target_beat}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    // Add a temporary highlight effect
                    var originalBg = paras[{target_beat}].style.backgroundColor;
                    paras[{target_beat}].style.backgroundColor = '#f0f9ff';
                    setTimeout(() => paras[{target_beat}].style.backgroundColor = originalBg, 2000);
                }}
            }}
        """
        ui.run_javascript(js_scroll)

    def _handle_key(self, e: events.KeyEventArguments):
        if e.key == ' ':
            self.is_panning_mode = e.action.keydown
            if self.is_panning_mode:
                self.canvas_container.classes(add='cursor-grab')
            else:
                self.canvas_container.classes(remove='cursor-grab cursor-grabbing')
                self.is_panning = False
        
        # Story Traversal Shortcuts
        if e.action.keydown:
            # Chapter Navigation (Ctrl + Shift + PageUp/Down)
            if e.modifiers.ctrl and e.modifiers.shift:
                slots = self.state.get_slots()
                current_idx = slots.index(self.state.current_slot)
                if e.key.page_up and current_idx > 0:
                    self._switch_slot(slots[current_idx - 1])
                elif e.key.page_down and current_idx < len(slots) - 1:
                    self._switch_slot(slots[current_idx + 1])
            
            # Beat Navigation (Ctrl + PageUp/Down)
            elif e.modifiers.ctrl:
                if e.key.page_up:
                    self._on_timeline_change(max(0, self.timeline_slider.value - 1))
                    self.timeline_slider.value = max(0, self.timeline_slider.value - 1)
                elif e.key.page_down:
                    tmap = self.state.get_timeline_map()
                    self._on_timeline_change(min(tmap['total_beats'] - 1, self.timeline_slider.value + 1))
                    self.timeline_slider.value = min(tmap['total_beats'] - 1, self.timeline_slider.value + 1)

    def _handle_canvas_mousedown(self, e: events.MouseEventArguments):
        if self.is_panning_mode:
            self.is_panning = True
            self.last_mouse = {'x': e.args['clientX'], 'y': e.args['clientY']}
            self.canvas_container.classes(add='cursor-grabbing')

    def _apply_pan(self):
        if hasattr(self, 'canvas_content') and self.canvas_content:
            self.canvas_content.style(f"transform: translate({self.pan_offset['x']}px, {self.pan_offset['y']}px);")

    def _toggle_importance_filter(self, level, value):
        self.importance_filter[level] = value
        self._refresh_canvas_content()

    def _refresh_canvas_content(self):
        self.canvas.refresh_canvas_content()

    def _switch_slot(self, name):
        self.active_beat_idx = -1
        self.state.switch_slot(name); self.build_canvas()

    def _delete_slot(self, name):
        if len(self.state.get_slots()) <= 1:
            ui.notify("Cannot delete the only chapter.", type='warning')
            return
        
        async def confirm():
            if self.state.delete_slot(name):
                ui.notify(f"Deleted chapter: {name}")
                self.build_canvas()
            dialog.close()

        with ui.dialog() as dialog, ui.card():
            ui.label(f"Delete chapter '{name}'?").classes('text-lg font-bold')
            ui.label("This will permanently remove all data for this chapter.")
            with ui.row().classes('w-full justify-end gap-2'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Delete', on_click=confirm).props('flat color=red')
        dialog.open()

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
        if self.is_panning:
            dx = e.args['clientX'] - self.last_mouse['x']
            dy = e.args['clientY'] - self.last_mouse['y']
            self.pan_offset['x'] += dx
            self.pan_offset['y'] += dy
            self.last_mouse = {'x': e.args['clientX'], 'y': e.args['clientY']}
            self._apply_pan()
            return

        if not self.active_entity: return
        dx = e.args['clientX'] - self.active_entity['smx']
        dy = e.args['clientY'] - self.active_entity['smy']
        self.active_entity['cx'] = self.active_entity['sox'] + dx
        self.active_entity['cy'] = self.active_entity['soy'] + dy
        self.active_entity['card'].style(f"left: {self.active_entity['cx']}px; top: {self.active_entity['cy']}px; transition: none;")

    def _handle_mouseup(self):
        if self.is_panning:
            self.is_panning = False
            if self.canvas_container:
                self.canvas_container.classes(remove='cursor-grabbing')
            return

        if not self.active_entity: return
        data = {'uid': self.active_entity['uid'], 'x': self.active_entity['cx'], 'y': self.active_entity['cy'], 'isEvent': self.active_entity['is_event']}
        self.active_entity['card'].classes(remove='z-50 shadow-2xl scale-105')
        self._handle_pos_update(data)
        self.active_entity = None

    def _handle_pos_update(self, data):
        if not self.state: return
        uid, x, y, is_ev = data['uid'], data['x'], data['y'], data.get('isEvent', False)
        
        # Apply Grid Snap
        if self.state.app_settings.snap_to_grid:
            gs = self.state.app_settings.grid_size
            x = round(x / gs) * gs
            y = round(y / gs) * gs

        if is_ev:
            for ev in self.state.events:
                if ev.uid == uid:
                    ev.x, ev.y = float(x), float(y)
                    self.state.save_event(ev); break
        else:
            self.state.update_state(uid, float(x), float(y), self.state.entity_states[uid].attributes)
        self._refresh_canvas_content()

    def _build_prose_panel(self):
        if not self.state: return
        with ui.column().classes('w-full h-full p-2 gap-2 overflow-hidden').props('id=prose-inner-container'):
            with ui.row().classes('w-full items-center gap-2 border-b border-slate-200 pb-2'):
                ui.icon('edit_note').classes('text-slate-400')
                self.prose_title = ui.input(value=self.state.prose.title, placeholder='Chapter Title') \
                    .classes('grow text-sm').props('dense borderless').on('change', self._save_prose)
                with ui.row().classes('gap-1'):
                    ui.button(icon='auto_awesome', on_click=self._prose_llm_action).props('flat dense round color=amber-7').tooltip('Extract Entities (LLM)')
                    ui.button(icon='save', on_click=lambda: self._save_prose(notify=True)).props('flat dense round color=blue-5').tooltip('Save')
            
            # Combine beats into one block for the rich editor
            content = "\n\n".join([b.text for b in self.state.prose.beats])
            self.prose_editor = ui.editor(value=content).classes('w-full flex-1 text-sm overflow-auto').props('id=prose-editor')
            self.prose_editor.props('flat square dense toolbar-rounded toolbar-bg=blue-grey-1 paragraph-tag=p')
            self.prose_editor.on_value_change(self._handle_prose_change)

            with ui.row().classes('w-full justify-between items-center px-1'):
                ui.label('Rich Editor').classes('text-[10px] text-slate-400 uppercase tracking-tighter')
                self.char_count_label = ui.label(f'Chars: {len(content)}').classes('text-[10px] text-slate-400')

    def _handle_prose_change(self, e):
        if hasattr(self, 'char_count_label'):
            self.char_count_label.text = f'Chars: {len(e.value or "")}'
        
        # Trigger immediate save and 'new beat' logic on 4 newlines
        # In Quill (ui.editor), this usually appears as 4 consecutive empty paragraphs
        if e.value and (e.value.count('<p><br></p>') >= 4 or e.value.count('\n\n\n\n') >= 4):
            # Clean up the extra newlines before saving to keep it tidy
            cleaned = e.value.replace('<p><br></p><p><br></p><p><br></p><p><br></p>', '<p><br></p>')
            cleaned = cleaned.replace('\n\n\n\n', '\n\n')
            if cleaned != e.value:
                self.prose_editor.value = cleaned
            
            self._save_prose(notify=True)
            ui.notify("New Beat committed", type='positive', position='top-right')
            return

        if self.prose_save_timer:
            self.prose_save_timer.cancel()
        self.prose_save_timer = ui.timer(1.5, self._save_prose, once=True)

    async def _prose_llm_action(self):
        content = self.prose_editor.value
        if not content or len(content) < 10:
            ui.notify("Prose is too short for analysis", type='warning')
            return
            
        from ..generators import analyze_prose
        ui.notify("Analyzing prose with LLM...", type='ongoing', spinner=True)
        
        result = await run.io_bound(analyze_prose,
            content,
            self.state.app_settings.llm_endpoint,
            self.state.app_settings.llm_model
        )
        
        if result:
            with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
                ui.label('LLM Analysis & Entity Extraction').classes('text-h6 font-bold')
                ui.markdown(result).classes('w-full max-h-96 overflow-y-auto p-4 bg-slate-50 rounded')
                with ui.row().classes('w-full justify-end'):
                    ui.button('Close', on_click=dialog.close).props('flat')
            dialog.open()
        else:
            ui.notify("LLM analysis failed", type='negative')

    def _save_prose(self, e=None, notify=False):
        if not self.state: return
        self.state.prose.title = self.prose_title.value
        content = self.prose_editor.value
        
        # Heuristic: split by double-newline to maintain 'Beats' for the timeline
        # We strip HTML tags for the internal text storage if possible, 
        # but ui.editor content is better kept as is if we want rich text.
        # For the Beat model, we'll store the rich text fragments.
        paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
        
        from ..models import Beat
        # Try to preserve UIDs for existing beats if they haven't changed much
        # For now, simple replacement is safer for consistency
        self.state.prose.beats = [Beat(text=p) for p in paragraphs]
        
        self.state.save_prose(self.state.prose)
        if notify:
            ui.notify("Prose saved!", type='positive', position='top')
        self.prose_save_timer = None

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=False, reload=False)

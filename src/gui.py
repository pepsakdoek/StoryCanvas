import os
import shutil
from typing import Optional, Dict, List, Type, Any
from nicegui import ui, events
from .storage import CanvasState, get_available_canvases, SAVES_DIR
from .models import Actor, Place, Item, Knowledge, Relationship, Importance, RelationshipType, Entity, AttributeTemplate, CanvasSettings

class StoryCanvasGUI:
    def __init__(self):
        self.state: Optional[CanvasState] = None
        self._setup_styles()
        self.container = ui.element('div').classes('w-full h-full')
        self.importance_filter = {level: True for level in Importance}
        self.type_filter = {
            'Actor': True,
            'Place': True,
            'Item': True,
            'Knowledge': True
        }

    def _setup_styles(self):
        ui.add_head_html('''
            <style>
                .canvas-container {
                    width: 100vw;
                    height: 100vh;
                    background-color: #f0f4f8;
                    position: relative;
                    overflow: hidden;
                }
                .grid-overlay {
                    position: absolute;
                    top: 0; left: 0;
                    width: 10000px; height: 10000px;
                    background-image: 
                        linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
                    background-size: 50px 50px;
                    pointer-events: none;
                    z-index: 0;
                }
                .entity-block {
                    width: 120px;
                    min-height: 80px;
                    background-color: #ffffff;
                    border: 2px solid #94a3b8;
                    border-radius: 12px;
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    position: absolute;
                    cursor: move;
                    z-index: 10;
                    font-size: 0.85rem;
                    padding: 8px;
                    user-select: none;
                    box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
                }
                .entity-actor { border-left: 6px solid #ef4444; }
                .entity-place { border-left: 6px solid #22c55e; }
                .entity-item { border-left: 6px solid #eab308; }
                .entity-knowledge { border-left: 6px solid #a855f7; }
                
                .relationship-line {
                    position: absolute;
                    height: 2px;
                    background-color: #94a3b8;
                    transform-origin: top left;
                    pointer-events: none;
                    z-index: 5;
                    opacity: 0.6;
                }
            </style>
            <script>
                window.startDrag = (e, id, uid) => {
                    const el = document.getElementById(id);
                    if (!el) return;
                    
                    const startX = e.clientX - el.offsetLeft;
                    const startY = e.clientY - el.offsetTop;

                    const move = (moveEvent) => {
                        el.style.left = (moveEvent.clientX - startX) + 'px';
                        el.style.top = (moveEvent.clientY - startY) + 'px';
                    };

                    const stop = () => {
                        document.removeEventListener('mousemove', move);
                        document.removeEventListener('mouseup', stop);
                        const x = parseInt(el.style.left);
                        const y = parseInt(el.style.top);
                        emitEvent('update_entity_pos', {uid: uid, x: x, y: y});
                    };

                    document.addEventListener('mousemove', move);
                    document.addEventListener('mouseup', stop);
                };
            </script>
        ''')
        ui.on('update_entity_pos', lambda e: self._handle_pos_update(e.args))

    def _handle_pos_update(self, data):
        if not self.state: return
        uid, x, y = data['uid'], data['x'], data['y']
        all_ents = self.state.actors + self.state.places + self.state.items + self.state.knowledge
        for e in all_ents:
            if e.uid == uid:
                e.x, e.y = float(x), float(y)
                self.state.save_entity(e)
                # We don't necessarily need to refresh the whole canvas content here 
                # because the JS already moved the element. 
                # But we might want to redraw relationships.
                self._draw_relationships()
                break

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
        self.build_canvas()

    def build_canvas(self):
        self.container.clear()
        with self.container:
            with ui.row().classes('absolute top-4 left-4 z-50 bg-white/90 backdrop-blur p-3 rounded-xl shadow border gap-4'):
                for etype in self.type_filter:
                    ui.checkbox(etype, value=self.type_filter[etype], 
                               on_change=lambda e, t=etype: self._toggle_type_filter(t, e.value))
                ui.separator().props('vertical')
                ui.button(icon='add', on_click=self.add_entity_dialog).props('round unelevated color=blue')
                ui.button(icon='link', on_click=self.add_relationship_dialog).props('round unelevated color=purple')
                ui.button(icon='settings', on_click=self.edit_settings_dialog).props('round flat color=slate-600')
                ui.button(icon='history', on_click=self.create_new_version).props('round flat color=slate-600')
                ui.button(icon='home', on_click=self.build_selector).props('round flat color=slate-600')

            self.canvas_container = ui.element('div').classes('canvas-container')
            with self.canvas_container:
                self._refresh_canvas_content()

    def _toggle_type_filter(self, etype, value):
        self.type_filter[etype] = value
        self._refresh_canvas_content()

    def _refresh_canvas_content(self):
        self.canvas_container.clear()
        with self.canvas_container:
            ui.element('div').classes('grid-overlay')
            self._draw_relationships()
            if self.type_filter['Actor']:
                for e in self.state.actors: self._add_entity_to_ui(e, 'entity-actor')
            if self.type_filter['Place']:
                for e in self.state.places: self._add_entity_to_ui(e, 'entity-place')
            if self.type_filter['Item']:
                for e in self.state.items: self._add_entity_to_ui(e, 'entity-item')
            if self.type_filter['Knowledge']:
                for e in self.state.knowledge: self._add_entity_to_ui(e, 'entity-knowledge')

    def _add_entity_to_ui(self, entity: Entity, css_class: str):
        with self.canvas_container:
            card = ui.card().classes(f'entity-block p-0 {css_class}') \
                .style(f'left: {entity.x}px; top: {entity.y}px')
            with card:
                ui.label(entity.name).classes('font-bold mt-1')
                if isinstance(entity, Actor):
                    ui.label(entity.importance.value).classes('text-[10px] uppercase text-slate-400')
                with ui.context_menu():
                    ui.menu_item('Delete', on_click=lambda: self.delete_entity(entity))
            
            # Using (e) => ... tells NiceGUI it is a JS handler.
            card.on('mousedown', f'(e) => window.startDrag(e, "{card.id}", "{entity.uid}")')

    def _draw_relationships(self):
        # We need to find elements or IDs. For simplicity, we redraw on state change.
        # However, for smooth drag, we'd need to update these lines in JS.
        # Redrawing them for now.
        all_ents = self.state.actors + self.state.places + self.state.items + self.state.knowledge
        uid_map = {e.uid: e for e in all_ents}
        
        # Clear existing lines (if we had a container for them)
        # For now, _refresh_canvas_content clears everything.
        
        for rel in self.state.relationships:
            src, dst = uid_map.get(rel.source_uid), uid_map.get(rel.target_uid)
            if src and dst:
                x1, y1 = src.x + 60, src.y + 40
                x2, y2 = dst.x + 60, dst.y + 40
                import math
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx) * 180 / math.pi
                ui.element('div').classes('relationship-line') \
                    .style(f'left: {x1}px; top: {y1}px; width: {dist}px; transform: rotate({angle}deg)') \
                    .tooltip(f"{rel.rel_type.value}: {rel.description}")

    def add_entity_dialog(self, default_type: Type[Entity] = Actor):
        form = {'type': default_type, 'name': '', 'importance': Importance.EXTRA, 'attributes': {}}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Entity').classes('text-h6')
            type_sel = ui.select({Actor: 'Actor', Place: 'Place', Item: 'Item', Knowledge: 'Knowledge'}, 
                                value=form['type'], on_change=lambda e: self._update_form_type(e.value, form, attr_cont, imp_sel))
            ui.input('Name', on_change=lambda e: form.update({'name': e.value}))
            
            imp_sel = ui.select({i: i.value.capitalize() for i in Importance}, 
                               label='Importance', value=form['importance'],
                               on_change=lambda e: form.update({'importance': e.value}))
            imp_sel.bind_visibility_from(type_sel, 'value', value=Actor)
            
            attr_cont = ui.column().classes('w-full gap-1')
            self._fill_attr_container(form['type'], attr_cont, form)
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: self._save_entity(dialog, form))
        dialog.open()

    def _update_form_type(self, new_type, form, container, imp_sel):
        form['type'] = new_type
        container.clear()
        self._fill_attr_container(new_type, container, form)

    def _fill_attr_container(self, etype, container, form):
        templates = []
        if etype == Actor: templates = self.state.settings.actor_attributes
        elif etype == Place: templates = self.state.settings.place_attributes
        elif etype == Item: templates = self.state.settings.item_attributes
        elif etype == Knowledge: templates = self.state.settings.knowledge_attributes
        with container:
            for t in templates:
                if t.enabled:
                    ui.input(t.name, on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})).props('dense outlined')

    def _save_entity(self, dialog, form):
        if not form['name']: return
        attrs = {k: v for k, v in form['attributes'].items() if v}
        args = {'name': form['name'], 'attributes': attrs, 'x': 200, 'y': 200}
        if form['type'] == Actor: entity = Actor(importance=form['importance'], **args)
        else: entity = form['type'](**args)
        self.state.save_entity(entity)
        self._refresh_canvas_content()
        dialog.close()

    def add_relationship_dialog(self):
        all_ents = self.state.actors + self.state.places + self.state.items + self.state.knowledge
        if len(all_ents) < 2: return
        form = {'src': all_ents[0].uid, 'dst': all_ents[1].uid, 'type': RelationshipType.SENTIMENT, 'desc': ''}
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Link Entities').classes('text-h6')
            ui.select({e.uid: e.name for e in all_ents}, label='Source', value=form['src'], on_change=lambda e: form.update({'src': e.value}))
            ui.select({e.uid: e.name for e in all_ents}, label='Target', value=form['dst'], on_change=lambda e: form.update({'dst': e.value}))
            ui.select({t: t.value for t in RelationshipType}, label='Type', value=form['type'], on_change=lambda e: form.update({'type': e.value}))
            ui.input('Description', on_change=lambda e: form.update({'desc': e.value}))
            ui.button('Connect', on_click=lambda: self._save_relationship(dialog, form))
        dialog.open()

    def _save_relationship(self, dialog, form):
        self.state.save_relationship(Relationship(source_uid=form['src'], target_uid=form['dst'], rel_type=form['type'], description=form['desc']))
        self._refresh_canvas_content()
        dialog.close()

    def edit_settings_dialog(self):
        with ui.dialog() as dialog, ui.card().classes('w-[500px]'):
            ui.label('Canvas Settings').classes('text-h6 mb-4')
            with ui.tabs() as tabs:
                ui.tab('Actors'); ui.tab('Places'); ui.tab('Items'); ui.tab('Knowledge')
            with ui.tab_panels(tabs, value='Actors').classes('w-full'):
                with ui.tab_panel('Actors'): self._build_settings_panel(self.state.settings.actor_attributes, dialog)
                with ui.tab_panel('Places'): self._build_settings_panel(self.state.settings.place_attributes, dialog)
                with ui.tab_panel('Items'): self._build_settings_panel(self.state.settings.item_attributes, dialog)
                with ui.tab_panel('Knowledge'): self._build_settings_panel(self.state.settings.knowledge_attributes, dialog)
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Save', on_click=lambda: self._save_settings(dialog))
        dialog.open()

    def _build_settings_panel(self, templates: List[AttributeTemplate], dialog):
        with ui.column().classes('w-full gap-2'):
            for t in templates:
                with ui.row().classes('w-full items-center justify-between'):
                    ui.input(value=t.name, on_change=lambda e, t=t: setattr(t, 'name', e.value)).props('dense outlined').classes('flex-grow mr-2')
                    ui.checkbox('Enabled', value=t.enabled, on_change=lambda e, t=t: setattr(t, 'enabled', e.value))
            ui.button('Add Attribute', on_click=lambda: self._add_empty_attr(templates, dialog)).props('flat icon=add')

    def _add_empty_attr(self, templates, dialog):
        templates.append(AttributeTemplate(name="New Attribute"))
        # Close and reopen to refresh the dialog UI correctly
        dialog.close()
        self.edit_settings_dialog()

    def _save_settings(self, dialog):
        self.state.save_settings(self.state.settings)
        ui.notify("Settings saved!")
        dialog.close()

    def create_new_version(self):
        from .cli import get_next_canvas_name
        new_name = get_next_canvas_name(self.state.name.split('_')[0])
        shutil.copytree(self.state.path, os.path.join(SAVES_DIR, new_name))
        self.load_canvas(new_name); ui.notify(f"Cloned to {new_name}")

    def delete_entity(self, entity):
        if isinstance(entity, Actor): self.state.actors.remove(entity)
        elif isinstance(entity, Place): self.state.places.remove(entity)
        elif isinstance(entity, Item): self.state.items.remove(entity)
        elif isinstance(entity, Knowledge): self.state.knowledge.remove(entity)
        self.state.relationships = [r for r in self.state.relationships if r.source_uid != entity.uid and r.target_uid != entity.uid]
        self.state._persist_entities(self.state.actors_file, self.state.actors)
        self.state._persist_entities(self.state.places_file, self.state.places)
        self.state._persist_entities(self.state.items_file, self.state.items)
        self.state._persist_entities(self.state.knowledge_file, self.state.knowledge)
        self.state._persist_relationships(); self._refresh_canvas_content()

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=False, reload=False)

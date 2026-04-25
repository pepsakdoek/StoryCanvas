import os
import shutil
from typing import Optional, Dict, List, Type, Any
from nicegui import ui, events
from .storage import CanvasState, get_available_canvases, SAVES_DIR
from .models import Actor, Place, Item, Knowledge, Relationship, Importance, RelationshipType, Entity

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
        self.selected_uid: Optional[str] = None

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
                    top: 0;
                    left: 0;
                    width: 10000px;
                    height: 10000px;
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
                    transition: border-color 0.2s, box-shadow 0.2s;
                }
                .entity-block:hover {
                    border-color: #3b82f6;
                    box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1);
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
                }
            </style>
            <script>
                window.startDrag = (event, id, entity_uid) => {
                    const el = document.getElementById(id);
                    if (!el) return;
                    
                    event.preventDefault();
                    let offsetX = event.clientX - el.offsetLeft;
                    let offsetY = event.clientY - el.offsetTop;

                    const move = (e) => {
                        el.style.left = (e.clientX - offsetX) + 'px';
                        el.style.top = (e.clientY - offsetY) + 'px';
                    };

                    const stop = (e) => {
                        document.removeEventListener('mousemove', move);
                        document.removeEventListener('mouseup', stop);
                        const x = parseInt(el.style.left);
                        const y = parseInt(el.style.top);
                        emitEvent('update_entity_pos', {uid: entity_uid, x: x, y: y});
                    };

                    document.addEventListener('mousemove', move);
                    document.addEventListener('mouseup', stop);
                };
            </script>
        ''')
        ui.on('update_entity_pos', lambda e: self._handle_pos_update(e.args))

    def _handle_pos_update(self, data):
        if not self.state: return
        uid = data['uid']
        x, y = data['x'], data['y']
        
        for collection in [self.state.actors, self.state.places, self.state.items, self.state.knowledge]:
            for entity in collection:
                if entity.uid == uid:
                    entity.x = float(x)
                    entity.y = float(y)
                    self.state.save_entity(entity)
                    self._refresh_canvas_content()
                    return

    def build_selector(self):
        self.container.clear()
        with self.container:
            with ui.card().classes('absolute-center w-96 p-8 shadow-2xl'):
                ui.label('StoryCanvas').classes('text-h4 mb-2 text-center w-full font-bold text-blue-600')
                ui.label('Narrative Engine').classes('text-subtitle1 mb-6 text-center w-full text-slate-500')
                
                canvases = get_available_canvases()
                
                with ui.column().classes('w-full gap-3'):
                    if canvases:
                        ui.label('Recent Canvases').classes('text-xs font-bold uppercase text-slate-400 mt-2')
                        for name in canvases:
                            ui.button(name, on_click=lambda n=name: self.load_canvas(n)) \
                                .classes('w-full').props('unelevated color=blue-5')
                    
                    ui.separator().classes('my-4')
                    
                    new_name_input = ui.input('New Canvas Name').classes('w-full').props('outlined dense')
                    ui.button('Create New Canvas', on_click=lambda: self.load_canvas(new_name_input.value)) \
                        .classes('w-full').props('unelevated color=green-6')
                    
                    ui.separator().classes('my-4')
                    ui.button('Exit System', on_click=lambda: os._exit(0)) \
                        .classes('w-full').props('outline color=negative')

    def load_canvas(self, name: str):
        if not name or not name.strip():
            ui.notify("Name is required", type='negative')
            return
        self.state = CanvasState(name.strip())
        self.build_canvas()

    def build_canvas(self):
        self.container.clear()
        
        with self.container:
            # Control Bar
            with ui.row().classes('absolute top-4 left-4 z-50 bg-white/80 backdrop-blur p-3 rounded-xl shadow-lg border border-slate-200 gap-4'):
                with ui.row().classes('items-center gap-2'):
                    ui.icon('filter_alt').classes('text-slate-500')
                    for etype in self.type_filter:
                        ui.checkbox(etype, value=self.type_filter[etype], 
                                   on_change=lambda e, t=etype: self._toggle_type_filter(t, e.value))
                
                ui.separator().props('vertical')
                
                with ui.row().classes('items-center gap-2'):
                    ui.button(icon='add', on_click=self.add_entity_dialog).props('round unelevated color=blue')
                    ui.button(icon='link', on_click=self.add_relationship_dialog).props('round unelevated color=purple')
                    ui.button(icon='history', on_click=self.create_new_version).props('round flat color=slate-600')
                    ui.button(icon='home', on_click=self.build_selector).props('round flat color=slate-600')

            self.canvas_container = ui.element('div').classes('canvas-container')
            with self.canvas_container:
                ui.element('div').classes('grid-overlay')
                self._refresh_canvas_content()

                with ui.context_menu():
                    ui.menu_item('Add Actor', on_click=lambda: self.add_entity_dialog(Actor))
                    ui.menu_item('Add Place', on_click=lambda: self.add_entity_dialog(Place))
                    ui.menu_item('Add Item', on_click=lambda: self.add_entity_dialog(Item))
                    ui.menu_item('Add Knowledge', on_click=lambda: self.add_entity_dialog(Knowledge))
                    ui.separator()
                    ui.menu_item('Back to Menu', on_click=self.build_selector)

    def _toggle_type_filter(self, etype, value):
        self.type_filter[etype] = value
        self._refresh_canvas_content()

    def _refresh_canvas_content(self):
        self.canvas_container.clear()
        with self.canvas_container:
            ui.element('div').classes('grid-overlay')
            
            # 1. Draw Relationships (Background)
            self._draw_relationships()
            
            # 2. Draw Entities (Foreground)
            if self.type_filter['Actor']:
                for actor in self.state.actors:
                    if self.importance_filter[actor.importance]:
                        self._add_entity_to_ui(actor, 'entity-actor')
            
            if self.type_filter['Place']:
                for place in self.state.places:
                    self._add_entity_to_ui(place, 'entity-place')
            
            if self.type_filter['Item']:
                for item in self.state.items:
                    self._add_entity_to_ui(item, 'entity-item')
            
            if self.type_filter['Knowledge']:
                for k in self.state.knowledge:
                    self._add_entity_to_ui(k, 'entity-knowledge')

    def _add_entity_to_ui(self, entity: Entity, css_class: str):
        with self.canvas_container:
            card = ui.card().classes(f'entity-block p-0 {css_class}') \
                .style(f'left: {entity.x}px; top: {entity.y}px')
            with card:
                ui.label(entity.name).classes('font-bold mt-1')
                if isinstance(entity, Actor):
                    ui.label(entity.importance.value).classes('text-[10px] uppercase text-slate-400')
                
                # Context menu for entity
                with ui.context_menu():
                    ui.menu_item('Edit', on_click=lambda: self.edit_entity_dialog(entity))
                    ui.menu_item('Delete', on_click=lambda: self.delete_entity(entity))

            # Fix for the drag and drop: use event object correctly
            card.on('mousedown', f'window.startDrag(event, "{card.id}", "{entity.uid}")')

    def _draw_relationships(self):
        # We need a way to find entities by UID for drawing lines
        all_entities = self.state.actors + self.state.places + self.state.items + self.state.knowledge
        uid_map = {e.uid: e for e in all_entities}
        
        for rel in self.state.relationships:
            src = uid_map.get(rel.source_uid)
            dst = uid_map.get(rel.target_uid)
            if src and dst:
                # Calculate center points
                x1, y1 = src.x + 60, src.y + 40
                x2, y2 = dst.x + 60, dst.y + 40
                
                import math
                dx = x2 - x1
                dy = y2 - y1
                dist = math.sqrt(dx*dx + dy*dy)
                angle = math.atan2(dy, dx) * 180 / math.pi
                
                ui.element('div').classes('relationship-line') \
                    .style(f'left: {x1}px; top: {y1}px; width: {dist}px; transform: rotate({angle}deg)') \
                    .tooltip(f"{rel.rel_type.value}: {rel.description}")

    def add_entity_dialog(self, default_type: Optional[Type[Entity]] = None):
        form = {'type': default_type or Actor, 'name': '', 'importance': Importance.EXTRA, 'attributes': {}}
        
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add New Entity').classes('text-h6')
            
            type_select = ui.select({Actor: 'Actor', Place: 'Place', Item: 'Item', Knowledge: 'Knowledge'}, 
                                  label='Type', value=form['type'], 
                                  on_change=lambda e: self._update_form_type(e.value, form, attr_container))
            
            name_input = ui.input('Name', on_change=lambda e: form.update({'name': e.value}))
            
            imp_select = ui.select({i: i.value.capitalize() for i in Importance}, 
                                  label='Importance', value=Importance.EXTRA,
                                  on_change=lambda e: form.update({'importance': e.value}))
            imp_select.bind_visibility_from(type_select, 'value', value=Actor)
            
            ui.label('Attributes').classes('text-xs font-bold mt-4 uppercase text-slate-400')
            attr_container = ui.column().classes('w-full gap-1')
            self._fill_attr_container(form['type'], attr_container, form)
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: self._save_entity(dialog, form))
        dialog.open()

    def _update_form_type(self, new_type, form, container):
        form['type'] = new_type
        container.clear()
        self._fill_attr_container(new_type, container, form)

    def _fill_attr_container(self, etype, container, form):
        templates = []
        if etype == Actor: templates = self.state.config.actor_attributes
        elif etype == Place: templates = self.state.config.place_attributes
        elif etype == Item: templates = self.state.config.item_attributes
        elif etype == Knowledge: templates = self.state.config.knowledge_attributes
        
        with container:
            for t in templates:
                ui.input(t.name, on_change=lambda e, n=t.name: form['attributes'].update({n: e.value})).props('dense outlined')

    def _save_entity(self, dialog, form):
        if not form['name'].strip():
            ui.notify("Name is required", type='negative')
            return
        
        attrs = {k: v for k, v in form['attributes'].items() if v and v.strip()}
        
        if form['type'] == Actor:
            entity = Actor(name=form['name'], importance=form['importance'], attributes=attrs, x=200, y=200)
        elif form['type'] == Place:
            entity = Place(name=form['name'], attributes=attrs, x=200, y=200)
        elif form['type'] == Item:
            entity = Item(name=form['name'], attributes=attrs, x=200, y=200)
        else:
            entity = Knowledge(name=form['name'], attributes=attrs, x=200, y=200)
            
        self.state.save_entity(entity)
        self._refresh_canvas_content()
        dialog.close()

    def add_relationship_dialog(self):
        all_entities = self.state.actors + self.state.places + self.state.items + self.state.knowledge
        if len(all_entities) < 2:
            ui.notify("Need at least 2 entities", type='warning')
            return
            
        form = {'src': all_entities[0].uid, 'dst': all_entities[1].uid, 'type': RelationshipType.SENTIMENT, 'desc': ''}
        
        with ui.dialog() as dialog, ui.card().classes('w-96'):
            ui.label('Add Relationship').classes('text-h6')
            
            ui.select({e.uid: e.name for e in all_entities}, label='Source', value=form['src'],
                     on_change=lambda e: form.update({'src': e.value}))
            ui.select({e.uid: e.name for e in all_entities}, label='Target', value=form['dst'],
                     on_change=lambda e: form.update({'dst': e.value}))
            ui.select({t: t.value for t in RelationshipType}, label='Type', value=form['type'],
                     on_change=lambda e: form.update({'type': e.value}))
            ui.input('Description', on_change=lambda e: form.update({'desc': e.value}))
            
            with ui.row().classes('w-full justify-end mt-4'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Connect', on_click=lambda: self._save_relationship(dialog, form))
        dialog.open()

    def _save_relationship(self, dialog, form):
        rel = Relationship(
            source_uid=form['src'],
            target_uid=form['dst'],
            rel_type=form['type'],
            description=form['desc']
        )
        self.state.save_relationship(rel)
        self._refresh_canvas_content()
        dialog.close()

    def create_new_version(self):
        from .cli import get_next_canvas_name
        new_name = get_next_canvas_name(self.state.name.split('_')[0])
        new_path = os.path.join(SAVES_DIR, new_name)
        shutil.copytree(self.state.path, new_path)
        ui.notify(f"Created version: {new_name}")
        self.load_canvas(new_name)

    def delete_entity(self, entity):
        # This is a bit complex as we need to remove it from the list and re-persist
        if isinstance(entity, Actor): self.state.actors.remove(entity)
        elif isinstance(entity, Place): self.state.places.remove(entity)
        elif isinstance(entity, Item): self.state.items.remove(entity)
        elif isinstance(entity, Knowledge): self.state.knowledge.remove(entity)
        
        # Also remove related relationships
        self.state.relationships = [r for r in self.state.relationships 
                                  if r.source_uid != entity.uid and r.target_uid != entity.uid]
        
        # Persist all
        self.state._persist_entities(self.state.actors_file, self.state.actors)
        self.state._persist_entities(self.state.places_file, self.state.places)
        self.state._persist_entities(self.state.items_file, self.state.items)
        self.state._persist_entities(self.state.knowledge_file, self.state.knowledge)
        self.state._persist_relationships()
        
        self._refresh_canvas_content()
        ui.notify(f"Deleted {entity.name}")

    def edit_entity_dialog(self, entity):
        # Implementation for editing (omitted for brevity but similar to add)
        ui.notify("Edit feature coming soon!")

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=False, reload=False)

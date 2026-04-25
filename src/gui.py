import os
from typing import Optional, Dict
from nicegui import ui
from .storage import CanvasState, get_available_canvases
from .models import Actor, Importance

class StoryCanvasGUI:
    def __init__(self):
        self.state: Optional[CanvasState] = None
        self._setup_styles()
        self.container = ui.element('div').classes('w-full h-full')
        self.importance_filter = {level: True for level in Importance}

    def _setup_styles(self):
        ui.add_head_html('''
            <style>
                .canvas-container {
                    width: 100vw;
                    height: 100vh;
                    background-color: #ffffff;
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
                    background-size: 100px 100px;
                    pointer-events: none;
                    z-index: 0;
                }
                .actor-block {
                    width: 80px;
                    height: 80px;
                    background-color: #e0e0e0;
                    border: 2px solid #9e9e9e;
                    border-radius: 8px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                    position: absolute;
                    cursor: move;
                    z-index: 10;
                    font-size: 0.8rem;
                    padding: 4px;
                    user-select: none;
                }
            </style>
            <script>
                window.startDrag = (id, actor_uid) => {
                    const el = document.getElementById(id);
                    if (!el) return;
                    
                    let offsetX, offsetY;

                    const move = (e) => {
                        el.style.left = (e.clientX - offsetX) + 'px';
                        el.style.top = (e.clientY - offsetY) + 'px';
                    };

                    const stop = (e) => {
                        document.removeEventListener('mousemove', move);
                        document.removeEventListener('mouseup', stop);
                        const x = parseInt(el.style.left);
                        const y = parseInt(el.style.top);
                        emitEvent('update_actor_pos', {uid: actor_uid, x: x, y: y});
                    };

                    offsetX = window.event.clientX - el.offsetLeft;
                    offsetY = window.event.clientY - el.offsetTop;
                    document.addEventListener('mousemove', move);
                    document.addEventListener('mouseup', stop);
                };
            </script>
        ''')
        ui.on('update_actor_pos', lambda e: self._handle_pos_update(e.args))

    def _handle_pos_update(self, data):
        if not self.state: return
        for actor in self.state.actors:
            if actor.uid == data['uid']:
                actor.x = data['x']
                actor.y = data['y']
                self.state.update_actor(actor)
                break

    def build_selector(self):
        self.container.clear()
        with self.container:
            with ui.card().classes('absolute-center w-96 p-8'):
                ui.label('StoryCanvas: Select Canvas').classes('text-h5 mb-4')
                canvases = get_available_canvases()
                
                with ui.column().classes('w-full gap-2'):
                    for name in canvases:
                        ui.button(name, on_click=lambda n=name: self.load_canvas(n)).classes('w-full')
                    
                    ui.separator().classes('my-4')
                    
                    new_name_input = ui.input('New Canvas Name').classes('w-full')
                    ui.button('Create & Open', on_click=lambda: self.load_canvas(new_name_input.value)).classes('w-full')
                    
                    ui.separator().classes('my-4')
                    ui.button('Exit', on_click=lambda: os._exit(0)).classes('w-full').props('outline color=negative')

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
            with ui.row().classes('absolute top-4 left-4 z-50 bg-white p-2 rounded shadow'):
                ui.label('Filters:').classes('font-bold self-center')
                for level in Importance:
                    ui.checkbox(level.value.capitalize(), value=self.importance_filter[level], 
                                on_change=lambda e, l=level: self._toggle_filter(l, e.value))
                ui.button('Menu', on_click=self.build_selector).props('small outline')

            self.canvas_container = ui.element('div').classes('canvas-container')
            with self.canvas_container:
                ui.element('div').classes('grid-overlay')
                self._refresh_actors()

                with ui.context_menu():
                    ui.menu_item('Add Actor', on_click=self.add_actor_dialog)
                    ui.separator()
                    ui.menu_item('Exit', on_click=lambda: os._exit(0))

    def _toggle_filter(self, level, value):
        self.importance_filter[level] = value
        self._refresh_actors()

    def _refresh_actors(self):
        self.canvas_container.clear()
        with self.canvas_container:
            ui.element('div').classes('grid-overlay')
            for actor in self.state.actors:
                if self.importance_filter[actor.importance]:
                    self.add_actor_to_ui(actor)

    def add_actor_to_ui(self, actor: Actor):
        with self.canvas_container:
            card = ui.card().classes('actor-block p-0 overflow-hidden') \
                .style(f'left: {actor.x}px; top: {actor.y}px')
            with card:
                ui.label(actor.name).classes('w-full h-full flex items-center justify-center')
                card.on('mousedown', f'window.startDrag("{card.id}", "{actor.uid}")')

    def add_actor_dialog(self):
        # Local state for the dialog inputs
        form_data = {
            'name': '',
            'importance': Importance.EXTRA,
            'attributes': {} # Name: Value
        }

        with ui.dialog() as dialog, ui.card().style('min-width: 500px'):
            ui.label('Add New Actor').classes('text-h6 mb-4')
            
            with ui.column().classes('w-full gap-4'):
                ui.input('Name', on_change=lambda e: form_data.update({'name': e.value})).classes('w-full')
                ui.select({i: i.value.capitalize() for i in Importance}, 
                         label='Importance', value=Importance.EXTRA,
                         on_change=lambda e: form_data.update({'importance': e.value})).classes('w-full')
                
                ui.separator()
                ui.label('Attributes (Optional)').classes('font-bold')
                
                attr_container = ui.column().classes('w-full gap-2')
                with attr_container:
                    # Show recommended attributes
                    for template in self.state.config.actor_attributes:
                        self._build_attr_input(template.name, form_data)
                
                # Button to add custom attributes
                with ui.row().classes('w-full items-center gap-2'):
                    new_attr_name = ui.input(placeholder='New custom attribute...').classes('flex-grow')
                    ui.button(icon='add', on_click=lambda: self._add_custom_attr_field(new_attr_name, attr_container, form_data)).props('flat')

            with ui.row().classes('w-full justify-end mt-6'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: self.save_new_actor(dialog, form_data))
        dialog.open()

    def _build_attr_input(self, name: str, form_data: dict):
        ui.input(name, on_change=lambda e: form_data['attributes'].update({name: e.value})).classes('w-full').props('dense')

    def _add_custom_attr_field(self, name_input, container, form_data):
        name = name_input.value.strip()
        if not name: return
        with container:
            self._build_attr_input(name, form_data)
        name_input.value = ''

    def save_new_actor(self, dialog, form_data):
        name = form_data.get('name', '').strip()
        if not name:
            ui.notify("Name is required", type='negative')
            return
        
        # Clean attributes (only save non-empty ones)
        attributes = {k: v for k, v in form_data['attributes'].items() if v and v.strip()}
        
        actor = Actor(
            name=name, 
            importance=form_data['importance'],
            attributes=attributes,
            x=150, y=150
        )
        self.state.save_actor(actor)
        self._refresh_actors()
        ui.notify(f"Actor '{name}' added!")
        dialog.close()

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=True, reload=False)

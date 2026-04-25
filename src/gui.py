import os
from typing import Optional
from nicegui import ui
from .storage import CanvasState, get_available_canvases
from .models import Actor

class StoryCanvasGUI:
    def __init__(self):
        self.state: Optional[CanvasState] = None
        self._setup_styles()
        self.container = ui.element('div').classes('w-full h-full')

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
        ''')

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

    def load_canvas(self, name: str):
        if not name or not name.strip():
            ui.notify("Name is required", type='negative')
            return
        self.state = CanvasState(name.strip())
        self.build_canvas()

    def build_canvas(self):
        self.container.clear()
        
        with self.container:
            self.canvas_container = ui.element('div').classes('canvas-container')
            with self.canvas_container:
                ui.element('div').classes('grid-overlay')
                
                # Initial load of actors
                for actor in self.state.actors:
                    self.add_actor_to_ui(actor)

                # Context Menu (Scope it to the container)
                with ui.context_menu():
                    ui.menu_item('Add Actor', on_click=self.add_actor_dialog)
                    ui.separator()
                    ui.menu_item('Back to Menu', on_click=self.build_selector)
                    ui.menu_item('Exit', on_click=lambda: os._exit(0))

    def add_actor_to_ui(self, actor: Actor):
        with self.canvas_container:
            ui.label(actor.name).classes('actor-block').style(f'left: {actor.x}px; top: {actor.y}px')

    def add_actor_dialog(self):
        with ui.dialog() as dialog, ui.card().style('min-width: 300px'):
            ui.label('Add New Actor').classes('text-h6')
            name_input = ui.input('Name').classes('w-full')
            desc_input = ui.textarea('Description').classes('w-full')
            
            with ui.row().classes('w-full justify-end'):
                ui.button('Cancel', on_click=dialog.close).props('flat')
                ui.button('Save', on_click=lambda: self.save_new_actor(dialog, name_input.value, desc_input.value))
        dialog.open()

    def save_new_actor(self, dialog, name, description):
        if name and name.strip():
            # For now, just drop it at a default position or middle of screen
            actor = Actor(name=name.strip(), description=description.strip(), x=150, y=150)
            self.state.save_actor(actor)
            self.add_actor_to_ui(actor)
            ui.notify(f"Actor '{name}' added!")
            dialog.close()
        else:
            ui.notify("Name is required", type='negative')

def run_gui():
    gui = StoryCanvasGUI()
    gui.build_selector()
    ui.run(title="StoryCanvas", port=8080, show=True)

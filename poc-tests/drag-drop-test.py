from nicegui import ui
import random

# --- DATA STATE ---
objects = {} 

class DraggableObject(ui.card):
    def __init__(self, obj_id, color, x=100, y=100):
        super().__init__()
        self.obj_id = obj_id
        # We use 'absolute' so it's positioned relative to the 'relative' canvas
        self.classes(f'bg-{color}-500 w-24 h-24 absolute shadow-xl cursor-move select-none')
        
        self.cur_x = x
        self.cur_y = y
        self.update_position()
        
        with self:
            ui.label(f'ID: {obj_id}').classes('text-white font-bold m-auto')
            ui.label('Fast Drag OK').classes('text-white text-[10px] m-auto opacity-70')

        self.dragging = False
        self.on('mousedown', self.handle_mousedown)

    def update_position(self):
        self.style(f'left: {self.cur_x}px; top: {self.cur_y}px; transition: none;')

    def handle_mousedown(self, e):
        self.dragging = True
        self.start_mouse_x = e.args['pageX']
        self.start_mouse_y = e.args['pageY']
        self.start_obj_x = self.cur_x
        self.start_obj_y = self.cur_y
        
        self.classes(remove='shadow-xl', add='shadow-2xl scale-105 z-50')
        # Tell the canvas this is the object we are currently moving
        canvas.active_object = self 

    def handle_mousemove(self, e):
        if not self.dragging:
            return
        # Calculate Delta from original click point
        dx = e.args['pageX'] - self.start_mouse_x
        dy = e.args['pageY'] - self.start_mouse_y
        
        self.cur_x = self.start_obj_x + dx
        self.cur_y = self.start_obj_y + dy
        self.update_position()

    def handle_mouseup(self):
        if self.dragging:
            self.dragging = False
            self.classes(remove='shadow-2xl scale-105 z-50', add='shadow-xl')
            ui.notify(f"Object {self.obj_id} settled at {int(self.cur_x)}, {int(self.cur_y)}", duration=1)
            canvas.active_object = None

def spawn_object():
    obj_id = len(objects)
    color = random.choice(['blue', 'red', 'green', 'purple', 'orange', 'pink'])
    objects[obj_id] = {'color': color}
    with canvas:
        DraggableObject(obj_id, color, random.randint(50, 300), random.randint(50, 300))

# --- UI LAYOUT ---
ui.query('body').classes('bg-slate-100 p-8')

with ui.column().classes('w-full max-w-4xl mx-auto gap-4'):
    with ui.row().classes('w-full items-center justify-between bg-white p-4 rounded-lg shadow'):
        ui.label('High-Speed Drag & Drop').classes('text-xl font-bold text-slate-700')
        ui.button('Add Object', on_click=spawn_object, icon='add').props('elevated')

    # The Canvas acts as the event catcher
    canvas = ui.element('div').classes('w-full h-[600px] bg-white rounded-xl border-2 border-slate-200 relative overflow-hidden shadow-inner')
    canvas.active_object = None

    # Canvas proxy functions to forward events to the active object
    def on_canvas_move(e):
        if canvas.active_object:
            canvas.active_object.handle_mousemove(e)

    def on_canvas_stop():
        if canvas.active_object:
            canvas.active_object.handle_mouseup()

    # Listening on the canvas ensures we don't lose the object if the mouse moves too fast
    canvas.on('mousemove', on_canvas_move)
    canvas.on('mouseup', on_canvas_stop)
    canvas.on('mouseleave', on_canvas_stop)
    
    with canvas:
        ui.label('DRAG AS FAST AS YOU WANT').classes('absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 text-slate-100 text-5xl font-black pointer-events-none text-center')

ui.run(title="D&D Test - High Speed", port=8081)

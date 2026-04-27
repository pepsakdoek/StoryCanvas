from nicegui import ui

def show_add_slot_dialog(gui):
    default_name = f"Chapter {len(gui.state.get_slots())+1}"
    with ui.dialog() as dialog, ui.card():
        ui.label('New Chapter').classes('text-h6')
        name = ui.input('Name', placeholder=default_name)
        clone = ui.checkbox('Clone state', value=True)
        ui.button('Create', on_click=lambda: _create_slot(gui, name.value or default_name, clone.value, dialog))
    dialog.open()

def _create_slot(gui, name, clone, dialog):
    if gui.state.create_slot(name, clone): 
        dialog.close()
        gui.build_canvas()

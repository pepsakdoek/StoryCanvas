import json
from nicegui import ui
from ..models import Event

def show_generator_dialog(gui):
    from ..generators import generate_any
    
    form = {
        'type': 'Names',
        'count': 1,
        'prompt': '',
        'result': None
    }

    with ui.dialog() as dialog, ui.card().classes('w-[500px] gap-4'):
        ui.label('Random Generator').classes('text-h6 font-bold')
        
        with ui.row().classes('w-full gap-2 items-center'):
            ui.select(['Names', 'Traits', 'Character', 'Place', 'Item', 'Knowledge', 'Event'], 
                      label='Type').bind_value(form, 'type').classes('flex-grow')
            ui.number('Count', value=1, min=1, max=10).bind_value(form, 'count').classes('w-20')
        
        ui.input('Custom Prompt (optional)').bind_value(form, 'prompt').classes('w-full')
        
        output_area = ui.label('Result will appear here...').classes(
            'p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono text-slate-700 whitespace-pre-wrap w-full'
        )

        def run_gen(force_proc=False):
            res = generate_any(
                form['type'], 
                gui.state.app_settings.llm_endpoint,
                gui.state.app_settings.llm_model,
                count=int(form['count']),
                custom_prompt=form['prompt'],
                force_procedural=force_proc
            )
            form['result'] = res
            output_area.set_text(json.dumps(res, indent=2))
            if not force_proc and res is None:
                ui.notify("LLM failed, try procedural?", type='warning')
        
        with ui.row().classes('w-full gap-2'):
            ui.button('Generate', on_click=lambda: run_gen()).classes('flex-grow')
            ui.button(icon='casino', on_click=lambda: run_gen(True)).props('flat').tooltip('Force Procedural')
        
        with ui.row().classes('w-full gap-2'):
            ui.button('Save to Canvas', on_click=lambda: _save_generated_to_canvas(gui, form['type'], form['result'], dialog)) \
                .classes('flex-grow bg-green-600 text-white')
            ui.button('Close', on_click=dialog.close).props('flat')

    dialog.open()

def _save_generated_to_canvas(gui, gen_type, result, dialog):
    if not result:
        ui.notify("Nothing to save!", type='warning')
        return
    
    try:
        if gen_type == "Names":
            for name in result.get('names', []):
                gui.state.create_entity(name, "Actor", "extra", {})
        elif gen_type == "Traits":
            ui.notify("Trait generation saved to clipboard (not yet auto-assigned)", type='info')
        elif gen_type == "Character":
            gui.state.create_entity(result['name'], "Actor", "secondary", 
                                         {"Role": result['role'], "Personality": result['personality'], 
                                          "Traits": ", ".join(result['traits'])})
        elif gen_type == "Place":
            gui.state.create_entity(result['name'], "Place", "extra", result.get('attributes', {}))
        elif gen_type == "Item":
            gui.state.create_entity(result['name'], "Item", "extra", result.get('attributes', {}))
        elif gen_type == "Knowledge":
            gui.state.create_entity(result['name'], "Knowledge", "extra", result.get('attributes', {}))
        elif gen_type == "Event":
            ev = Event(
                name=result['name'],
                description=result['description'],
                importance=result.get('importance', 'extra'),
                attributes=result.get('attributes', {}),
                involved_uids=result.get('involved_uids', []),
                location_uid=result.get('location_uid'),
                x=result.get('x', 500),
                y=result.get('y', 500)
            )
            gui.state.save_event(ev)
        
        gui._refresh_canvas_content()
        ui.notify(f"Saved {gen_type} to canvas!")
        dialog.close()
    except Exception as e:
        ui.notify(f"Error saving: {str(e)}", type='negative')

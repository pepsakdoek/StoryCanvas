from nicegui import ui
from ..models import AttributeTemplate
from ..storage import save_app_settings

def show_settings_dialog(gui):
    with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
        ui.label('Settings').classes('text-h6 mb-4')
        with ui.tabs() as tabs: 
            ui.tab('App Settings')
            ui.tab('Story Settings')
            ui.tab('Attributes')
        
        with ui.tab_panels(tabs, value='App Settings').classes('w-full'):
            with ui.tab_panel('App Settings'):
                ui.label('Technical configuration (Global)').classes('text-caption text-slate-500 mb-4')
                with ui.column().classes('w-full gap-4'):
                    ui.label('LLM (Local Ollama)').classes('font-bold text-sm')
                    ui.input('Endpoint', value=gui.state.app_settings.llm_endpoint, 
                             on_change=lambda e: setattr(gui.state.app_settings, 'llm_endpoint', e.value)).classes('w-full')
                    ui.input('Model', value=gui.state.app_settings.llm_model, 
                             on_change=lambda e: setattr(gui.state.app_settings, 'llm_model', e.value)).classes('w-full')
                    
                    ui.separator()
                    ui.label('Grid & Snap').classes('font-bold text-sm')
                    ui.checkbox('Snap to Grid', value=gui.state.app_settings.snap_to_grid, 
                                on_change=lambda e: setattr(gui.state.app_settings, 'snap_to_grid', e.value))
                    ui.number('Grid Size', value=gui.state.app_settings.grid_size, suffix='px',
                              on_change=lambda e: setattr(gui.state.app_settings, 'grid_size', int(e.value)))

            with ui.tab_panel('Story Settings'):
                ui.label('Narrative structure (This Story)').classes('text-caption text-slate-500 mb-4')
                ui.label('Importance Levels').classes('font-bold text-sm mb-2')
                for i, level in enumerate(gui.state.settings.importance_levels):
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.input(value=level, on_change=lambda e, idx=i: _update_imp_name(gui, idx, e.value)).props('dense outlined').classes('flex-grow')
                        ui.button(icon='delete', on_click=lambda idx=i: _remove_imp_level(gui, idx, dialog)).props('flat color=red')
                ui.button('Add Level', on_click=lambda: _add_imp_level(gui, dialog)).props('flat icon=add').classes('mb-4')

            with ui.tab_panel('Attributes'):
                ui.label('Default attribute schemas per entity type').classes('text-caption text-slate-500 mb-4')
                _build_attributes_manager(gui)

        ui.button('Save All Settings', on_click=lambda: _save_settings(gui, dialog)).classes('w-full bg-blue-600 text-white mt-4')
    dialog.open()

def _build_attributes_manager(gui):
    with ui.tabs() as etabs:
        ui.tab('Actors'); ui.tab('Places'); ui.tab('Items'); ui.tab('Knowledge'); ui.tab('Events')
    
    with ui.tab_panels(etabs, value='Actors').classes('w-full'):
        _attr_tab_panel(gui, 'Actors', gui.state.settings.actor_attributes)
        _attr_tab_panel(gui, 'Places', gui.state.settings.place_attributes)
        _attr_tab_panel(gui, 'Items', gui.state.settings.item_attributes)
        _attr_tab_panel(gui, 'Knowledge', gui.state.settings.knowledge_attributes)
        _attr_tab_panel(gui, 'Events', gui.state.settings.event_attributes)

def _attr_tab_panel(gui, label, templates):
    with ui.tab_panel(label):
        with ui.column().classes('w-full gap-2'):
            for i, t in enumerate(templates):
                with ui.card().classes('w-full p-2 bg-slate-50'):
                    with ui.row().classes('w-full items-center gap-2'):
                        ui.input('Name', value=t.name, on_change=lambda e, idx=i: setattr(templates[idx], 'name', e.value)).classes('flex-grow')
                        ui.select(['text', 'number', 'select'], label='Type', value=t.attr_type,
                                  on_change=lambda e, idx=i: setattr(templates[idx], 'attr_type', e.value)).classes('w-24')
                        ui.checkbox('Req', value=t.required, on_change=lambda e, idx=i: setattr(templates[idx], 'required', e.value)).tooltip('Required')
                        ui.button(icon='delete', on_click=lambda idx=i: _remove_attr(templates, idx)).props('flat color=red dense')
                    
                    if t.attr_type == 'select':
                        options_str = ", ".join(t.options)
                        ui.input('Options (comma separated)', value=options_str, 
                                 on_change=lambda e, idx=i: setattr(templates[idx], 'options', [s.strip() for s in e.value.split(',')])).classes('w-full text-xs')

            ui.button('Add Attribute', on_click=lambda: _add_attr(templates)).props('flat icon=add').classes('mt-2')

def _add_attr(templates):
    templates.append(AttributeTemplate(name="New Attribute"))
    ui.notify("Attribute added. Save to apply.")

def _remove_attr(templates, idx):
    templates.pop(idx)
    ui.notify("Attribute removed. Save to apply.")

def _update_imp_name(gui, idx, val):
    gui.state.settings.importance_levels[idx] = val

def _add_imp_level(gui, dialog):
    gui.state.settings.importance_levels.append("new level")
    dialog.close()
    show_settings_dialog(gui)

def _remove_imp_level(gui, idx, dialog):
    gui.state.settings.importance_levels.pop(idx)
    dialog.close()
    show_settings_dialog(gui)

def _save_settings(gui, dialog): 
    gui.state.save_settings(gui.state.settings)
    save_app_settings(gui.state.app_settings)
    dialog.close()

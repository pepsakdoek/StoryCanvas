from nicegui import ui
from ..models import AttributeTemplate, AttributeType
from ..storage import save_app_settings

def show_settings_dialog(gui):
    # Set a fixed max-height for the dialog card to ensure it fits the screen
    # and use flex-column to manage internal layout
    with ui.dialog() as dialog, ui.card().classes('w-[700px] h-[700px] max-h-[90vh] flex-nowrap p-0').props('id=settings-dialog-card'):
        with ui.column().classes('w-full h-full p-4 gap-0'):
            ui.label('Settings').classes('text-h6 mb-2').props('id=settings-title')
            
            with ui.tabs().classes('w-full').props('id=settings-tabs') as tabs: 
                ui.tab('App Settings').props('id=tab-app')
                ui.tab('Story Settings').props('id=tab-story')
                ui.tab('Attributes').props('id=tab-attr')
            
            # The tab_panels should take the remaining space and scroll internally
            with ui.tab_panels(tabs, value='App Settings').classes('w-full flex-1 overflow-hidden').props('id=settings-tab-panels'):
                with ui.tab_panel('App Settings').props('id=panel-app'):
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

                with ui.tab_panel('Story Settings').props('id=panel-story'):
                    ui.label('Narrative structure (This Story)').classes('text-caption text-slate-500 mb-4')
                    ui.label('Importance Levels').classes('font-bold text-sm mb-2')
                    with ui.scroll_area().classes('w-full flex-1 h-[400px]'):
                        for i, level in enumerate(gui.state.settings.importance_levels):
                            with ui.row().classes('w-full items-center gap-2 mb-2'):
                                ui.input(value=level, on_change=lambda e, idx=i: _update_imp_name(gui, idx, e.value)).props('dense outlined').classes('flex-grow')
                                ui.button(icon='delete', on_click=lambda idx=i: _remove_imp_level(gui, idx, dialog)).props('flat color=red')
                        ui.button('Add Level', on_click=lambda: _add_imp_level(gui, dialog)).props('flat icon=add').classes('w-full border border-dashed')

                with ui.tab_panel('Attributes').props('id=panel-attr'):
                    ui.label('Default attribute schemas per entity type').classes('text-caption text-slate-500 mb-2')
                    _render_attributes_content(gui)

            ui.button('Save All Settings', on_click=lambda: _save_settings(gui, dialog)).classes('w-full bg-blue-600 text-white mt-4').props('id=save-settings-btn')
    dialog.open()

@ui.refreshable
def _render_attributes_content(gui):
    with ui.tabs().classes('w-full bg-slate-100 rounded-t').props('id=attr-entity-tabs') as etabs:
        ui.tab('Actors'); ui.tab('Places'); ui.tab('Items'); ui.tab('Knowledge'); ui.tab('Events')
    
    etabs.bind_value(gui, 'active_attr_tab')

    with ui.tab_panels(etabs, value=gui.active_attr_tab).classes('w-full flex-1 overflow-hidden border').props('id=attr-entity-panels'):
        _attr_tab_panel(gui, 'Actors', gui.state.settings.actor_attributes)
        _attr_tab_panel(gui, 'Places', gui.state.settings.place_attributes)
        _attr_tab_panel(gui, 'Items', gui.state.settings.item_attributes)
        _attr_tab_panel(gui, 'Knowledge', gui.state.settings.knowledge_attributes)
        _attr_tab_panel(gui, 'Events', gui.state.settings.event_attributes)

def _attr_tab_panel(gui, label, templates):
    with ui.tab_panel(label).classes('p-0'):
        # Use scroll_area for better scroll control than just overflow-y-auto
        with ui.scroll_area().classes('w-full h-[400px] p-4'):
            with ui.column().classes('w-full gap-2 pb-8'):
                for i, t in enumerate(templates):
                    with ui.card().classes('w-full p-2 bg-slate-50 border-none shadow-none'):
                        with ui.row().classes('w-full items-center gap-2'):
                            ui.input('Name', value=t.name, on_change=lambda e, idx=i: setattr(templates[idx], 'name', e.value)).classes('flex-grow')
                            ui.select(['text', 'number', 'select'], label='Type', value=t.attr_type,
                                      on_change=lambda e, idx=i, templ=templates: _change_attr_type(templ, idx, e.value)).classes('w-32')
                            ui.checkbox('Req', value=t.required, on_change=lambda e, idx=i: setattr(templates[idx], 'required', e.value)).tooltip('Required')
                            ui.button(icon='delete', on_click=lambda idx=i, templ=templates: _remove_attr(templ, idx)).props('flat color=red dense')
                        
                        if t.attr_type == 'select':
                            with ui.row().classes('w-full items-center gap-4'):
                                options_str = "; ".join(t.options)
                                ui.input('Options (delimited by ;)', value=options_str, 
                                         on_change=lambda e, idx=i: setattr(templates[idx], 'options', [s.strip() for s in e.value.split(';') if s.strip()])).classes('flex-grow text-xs')
                                ui.checkbox('Allow Adding Options', value=t.allow_custom,
                                            on_change=lambda e, idx=i: setattr(templates[idx], 'allow_custom', e.value)).classes('text-xs').tooltip('Allow adding new options while editing entities')

                ui.button('Add Attribute', on_click=lambda templ=templates: _add_attr(templ)).props('flat icon=add').classes('mt-2 w-full border border-dashed')

def _change_attr_type(templates, idx, val):
    templates[idx].attr_type = val
    _render_attributes_content.refresh()

def _add_attr(templates):
    templates.append(AttributeTemplate(name="New Attribute"))
    _render_attributes_content.refresh()
    ui.notify("Attribute added. Save to apply.")

def _remove_attr(templates, idx):
    templates.pop(idx)
    _render_attributes_content.refresh()
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

from .entity_dialog import show_add_entity_dialog, show_edit_entity_dialog
from .event_dialog import show_add_event_dialog, show_edit_event_dialog
from .relationship_dialog import show_add_relationship_dialog, show_edit_relationship_dialog
from .slot_dialog import show_add_slot_dialog
from .settings_dialog import show_settings_dialog
from .generator_dialog import show_generator_dialog

class DialogManager:
    def __init__(self, gui):
        self.gui = gui

    def add_entity_dialog(self, etype: str):
        show_add_entity_dialog(self.gui, etype)

    def edit_entity_dialog(self, identity, state):
        show_edit_entity_dialog(self.gui, identity, state)

    def add_event_dialog(self):
        show_add_event_dialog(self.gui)

    def edit_event_dialog(self, ev):
        show_edit_event_dialog(self.gui, ev)

    def add_relationship_dialog(self):
        show_add_relationship_dialog(self.gui)

    def edit_relationship_dialog(self, rel):
        show_edit_relationship_dialog(self.gui, rel)

    def add_slot_dialog(self):
        show_add_slot_dialog(self.gui)

    def edit_settings_dialog(self):
        show_settings_dialog(self.gui)

    def open_generator_dialog(self):
        show_generator_dialog(self.gui)

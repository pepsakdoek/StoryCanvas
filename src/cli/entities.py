import json
from ..models import Event
from .utils import list_all_entities, list_all_events, _select_importance, input_attributes

def entity_menu(state):
    while True:
        print("\n--- Entity Management ---")
        print("1. Add Entity")
        print("2. Edit Entity")
        print("3. Delete Entity")
        print("4. Back")
        cmd = input("Select: ").strip()
        
        if cmd == "1":
            print("\nSelect Type: 1. Actor, 2. Place, 3. Item, 4. Knowledge")
            t_choice = input("Type: ").strip()
            etype_map = {"1": "Actor", "2": "Place", "3": "Item", "4": "Knowledge"}
            etype = etype_map.get(t_choice)
            if not etype: continue
            
            name = input(f"Enter {etype.lower()} name: ").strip()
            if not name: continue
            
            importance = _select_importance(state)
            
            attr_templates = {
                "Actor": state.settings.actor_attributes,
                "Place": state.settings.place_attributes,
                "Item": state.settings.item_attributes,
                "Knowledge": state.settings.knowledge_attributes
            }[etype]
            
            attrs = input_attributes(attr_templates)
            state.create_entity(name, etype, importance, attrs)
            print(f"Created {etype}: {name}")

        elif cmd == "2":
            entities = list_all_entities(state)
            if not entities: continue
            choice = input("Select entity to edit (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entities):
                    identity = entities[idx]
                    estat = state.entity_states[identity.uid]
                    
                    print(f"\nEditing {identity.name} ({identity.entity_type})")
                    new_name = input(f"New Name (current: '{identity.name}'): ").strip() or identity.name
                    new_imp = _select_importance(state, current=identity.importance)
                    
                    new_x = input(f"X position (current: {estat.x}): ").strip()
                    new_y = input(f"Y position (current: {estat.y}): ").strip()
                    x = float(new_x) if new_x else estat.x
                    y = float(new_y) if new_y else estat.y
                    
                    attr_templates = {
                        "Actor": state.settings.actor_attributes,
                        "Place": state.settings.place_attributes,
                        "Item": state.settings.item_attributes,
                        "Knowledge": state.settings.knowledge_attributes
                    }[identity.entity_type]
                    
                    new_attrs = input_attributes(attr_templates, current_values=estat.attributes)
                    
                    state.update_identity(identity.uid, new_name, new_imp)
                    state.update_state(identity.uid, x, y, new_attrs)
                    print("Entity updated.")
            except (ValueError, IndexError):
                print("Invalid selection.")

        elif cmd == "3":
            entities = list_all_entities(state)
            if not entities: continue
            choice = input("Select entity to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entities):
                    confirm = input(f"Delete '{entities[idx].name}'? (y/n): ").lower()
                    if confirm == 'y':
                        state.delete_entity(entities[idx].uid)
                        print("Entity deleted.")
            except:
                print("Invalid selection.")
        
        elif cmd == "4": break

def event_menu(state):
    while True:
        print("\n--- Event Management ---")
        print("1. Add Event")
        print("2. Edit Event")
        print("3. Delete Event")
        print("4. Back")
        cmd = input("Select: ").strip()
        
        if cmd == "1":
            name = input("Enter event name: ").strip()
            if not name: continue
            desc = input("Description: ").strip()
            importance = _select_importance(state)
            attrs = input_attributes(state.settings.event_attributes)
            ev = Event(name=name, description=desc, importance=importance, attributes=attrs)
            state.save_event(ev)
            print("Event added.")

        elif cmd == "2":
            events = list_all_events(state)
            if not events: continue
            choice = input("Select event to edit (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(events):
                    ev = events[idx]
                    print(f"\nEditing Event: {ev.name}")
                    ev.name = input(f"New Name (current: '{ev.name}'): ").strip() or ev.name
                    ev.description = input(f"New Description (current: '{ev.description}'): ").strip() or ev.description
                    ev.importance = _select_importance(state, current=ev.importance)
                    
                    new_x = input(f"X position (current: {ev.x}): ").strip()
                    new_y = input(f"Y position (current: {ev.y}): ").strip()
                    ev.x = float(new_x) if new_x else ev.x
                    ev.y = float(new_y) if new_y else ev.y
                    
                    ev.attributes = input_attributes(state.settings.event_attributes, current_values=ev.attributes)
                    state.save_event(ev)
                    print("Event updated.")
            except:
                print("Invalid selection.")

        elif cmd == "3":
            events = list_all_events(state)
            if not events: continue
            choice = input("Select event to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(events):
                    uid = events[idx].uid
                    state.events = [e for e in state.events if e.uid != uid]
                    with open(state.events_file, "w") as f:
                        json.dump([e.model_dump() for e in state.events], f, indent=4)
                    print("Event deleted.")
            except:
                print("Invalid selection.")
        
        elif cmd == "4": break

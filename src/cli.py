import os
import shutil
import uuid
import json
from .storage import CanvasState, get_available_canvases, SAVES_DIR, save_app_settings
from .models import Relationship, DefaultImportance, RelationshipType, EntityIdentity, EntityState, Event, AttributeType, AttributeTemplate

def get_next_canvas_name(base_name: str) -> str:
    canvases = get_available_canvases()
    name = base_name.split('_')[0]
    i = 1
    while f"{name}_{i}" in canvases:
        i += 1
    return f"{name}_{i}"

def input_attributes(templates, current_values=None):
    attributes = current_values.copy() if current_values else {}
    if not templates:
        return attributes
    
    print("\n--- Editing Attributes ---")
    for template in templates:
        if not template.enabled:
            continue
        
        current_val = attributes.get(template.name, "")
        label = f"{template.name}{' *' if template.required else ''}"
        if template.attr_type == 'select':
            print(f"{label} Options: {', '.join(template.options)}")
        
        prompt = f"{label} (current: '{current_val}'): "
        val = input(prompt).strip()
        
        if not val:
            if current_val:
                val = current_val # Keep existing
            elif template.required:
                print(f"Error: {template.name} is required.")
                while not val:
                    val = input(f"{label}: ").strip()
        
        if val:
            attributes[template.name] = val
    
    while True:
        print("\nCustom attributes (currently: " + ", ".join([f"{k}={v}" for k,v in attributes.items() if k not in [t.name for t in templates]]) + ")")
        attr_name = input("Add/Edit custom attribute name (or Enter to finish): ").strip()
        if not attr_name:
            break
        attr_val = input(f"{attr_name} value: ").strip()
        if attr_val:
            attributes[attr_name] = attr_val
        elif attr_name in attributes:
            confirm = input(f"Delete attribute '{attr_name}'? (y/n): ").lower()
            if confirm == 'y':
                del attributes[attr_name]

    return attributes

def list_all_entities(state: CanvasState):
    entities = []
    idx = 1
    print("\n--- Entities ---")
    
    by_type = {}
    for uid, s in state.entity_states.items():
        identity = state.registry.entities.get(uid)
        if identity:
            etype = identity.entity_type
            if etype not in by_type: by_type[etype] = []
            by_type[etype].append((identity, s))

    for etype in sorted(by_type.keys()):
        print(f"\n[{etype}s]")
        for identity, s in by_type[etype]:
            info = f"{idx}. [{identity.uid[:8]}] {identity.name}"
            info += f" (Imp: {identity.importance}, Pos: {s.x}, {s.y})"
            print(info)
            entities.append(identity)
            idx += 1
            
    return entities

def list_all_events(state: CanvasState):
    print("\n--- Events ---")
    for i, ev in enumerate(state.events):
        print(f"{i+1}. [{ev.uid[:8]}] {ev.name} (Imp: {ev.importance}, Pos: {ev.x}, {ev.y})")
    return state.events

def run_cli():
    print("--- StoryCanvas CLI ---")
    canvases = get_available_canvases()
    
    print("\nAvailable Canvases:")
    for i, c in enumerate(canvases):
        print(f"{i+1}. {c}")
    print(f"{len(canvases)+1}. [Create New Canvas]")
    
    choice = input("\nSelect a canvas (number): ").strip()
    
    canvas_name = ""
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(canvases):
            canvas_name = canvases[idx]
        elif idx == len(canvases):
            canvas_name = input("Enter new canvas name: ").strip()
        else:
            print("Invalid selection.")
            return
    except ValueError:
        print("Invalid input.")
        return

    if not canvas_name:
        print("Canvas name cannot be empty.")
        return

    state = CanvasState(canvas_name)
    print(f"\nActive Canvas: {canvas_name}")
    
    while True:
        print(f"\n--- {canvas_name} [{state.current_slot}] Main Menu ---")
        print("1. Entities (Add/Edit/Delete)")
        print("2. Events (Add/Edit/Delete)")
        print("3. Relationships (Add/Edit/Delete)")
        print("4. Chapters (Add/Switch/Delete)")
        print("5. Prose (View/Edit)")
        print("6. Generators (Random Content)")
        print("7. Settings (App/Story/Attributes)")
        print("8. Auto-Arrange Canvas")
        print("9. List Everything")
        print("0. Exit")
        cmd = input("Select category: ").strip()
        
        if cmd == "1": _entity_menu(state)
        elif cmd == "2": _event_menu(state)
        elif cmd == "3": _relationship_menu(state)
        elif cmd == "4": _chapter_menu(state)
        elif cmd == "5": _edit_prose_cli(state)
        elif cmd == "6": _generator_cli(state)
        elif cmd == "7": _settings_menu(state)
        elif cmd == "8":
            state.auto_arrange()
            print("Canvas auto-arranged.")
        elif cmd == "9": _list_everything(state)
        elif cmd == "0": break

def _entity_menu(state: CanvasState):
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

def _event_menu(state: CanvasState):
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

def _relationship_menu(state: CanvasState):
    while True:
        print("\n--- Relationship Management ---")
        print("1. Add Relationship")
        print("2. Edit Relationship")
        print("3. Delete Relationship")
        print("4. Back")
        cmd = input("Select: ").strip()
        
        if cmd == "1":
            entities = _get_all_linkable(state)
            if len(entities) < 2:
                print("Need at least 2 entities/events to create a relationship.")
                continue
            
            try:
                for i, e in enumerate(entities):
                    print(f"{i+1}. {e['name']} ({e['type']})")
                src_idx = int(input("\nSelect source (number): ")) - 1
                dst_idx = int(input("Select target (number): ")) - 1
                
                print("\nRelationship Types:")
                for i, t in enumerate(RelationshipType):
                    print(f"{i+1}. {t.value}")
                rel_choice = input("Select type: ").strip()
                rel_type = list(RelationshipType)[int(rel_choice)-1] if rel_choice else RelationshipType.SENTIMENT
                
                description = input("Enter description: ").strip()
                
                rel = Relationship(
                    source_uid=entities[src_idx]['uid'],
                    target_uid=entities[dst_idx]['uid'],
                    rel_type=rel_type,
                    description=description
                )
                state.save_relationship(rel)
                print("Relationship added.")
            except:
                print("Invalid selection.")

        elif cmd == "2":
            if not state.relationships:
                print("No relationships found.")
                continue
            for i, r in enumerate(state.relationships):
                print(f"{i+1}. {r.source_uid[:8]} --({r.rel_type.value})--> {r.target_uid[:8]} : {r.description}")
            
            choice = input("Select relationship to edit (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(state.relationships):
                    rel = state.relationships[idx]
                    print(f"\nEditing Relationship: {rel.uid[:8]}")
                    
                    print("\nChange entities? (y/n)")
                    if input().lower() == 'y':
                        entities = _get_all_linkable(state)
                        for i, e in enumerate(entities):
                            print(f"{i+1}. {e['name']} ({e['type']})")
                        rel.source_uid = entities[int(input("New source: "))-1]['uid']
                        rel.target_uid = entities[int(input("New target: "))-1]['uid']

                    print("\nRelationship Types:")
                    for i, t in enumerate(RelationshipType):
                        print(f"{i+1}. {t.value} {'(current)' if rel.rel_type == t else ''}")
                    rel_choice = input("Select new type (Enter to skip): ").strip()
                    if rel_choice:
                        rel.rel_type = list(RelationshipType)[int(rel_choice)-1]
                    
                    rel.description = input(f"New Description (current: '{rel.description}'): ").strip() or rel.description
                    state.save_relationships()
                    print("Relationship updated.")
            except:
                print("Invalid selection.")

        elif cmd == "3":
            for i, r in enumerate(state.relationships):
                print(f"{i+1}. {r.source_uid[:8]} -> {r.target_uid[:8]} ({r.description})")
            choice = input("Select relationship to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(state.relationships):
                    uid = state.relationships[idx].uid
                    state.relationships = [r for r in state.relationships if r.uid != uid]
                    state.save_relationships()
                    print("Relationship deleted.")
            except:
                print("Invalid selection.")
        
        elif cmd == "4": break

def _chapter_menu(state: CanvasState):
    while True:
        print("\n--- Chapter Management ---")
        print("1. List Chapters")
        print("2. Create New Chapter")
        print("3. Switch Chapter")
        print("4. Delete Chapter")
        print("5. Back")
        cmd = input("Select: ").strip()
        
        if cmd == "1":
            for s in state.get_slots():
                print(f"- {s} {'(current)' if s == state.current_slot else ''}")
        
        elif cmd == "2":
            new_name = input("Enter name for new Chapter: ").strip()
            if new_name:
                clone = input("Clone current state? (y/n, default y): ").lower() != 'n'
                if state.create_slot(new_name, clone_current=clone):
                    print(f"Created and switched to chapter: {new_name}")
                else:
                    print("Chapter already exists or failed to create.")

        elif cmd == "3":
            slots = state.get_slots()
            for i, s in enumerate(slots):
                print(f"{i+1}. {s} {'(current)' if s == state.current_slot else ''}")
            choice = input("Select chapter (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(slots):
                    state.switch_slot(slots[idx])
                    print(f"Switched to chapter: {slots[idx]}")
            except:
                print("Invalid selection.")

        elif cmd == "4":
            slots = state.get_slots()
            if len(slots) <= 1:
                print("Cannot delete the only chapter.")
                continue
            for i, s in enumerate(slots):
                print(f"{i+1}. {s}")
            choice = input("Select chapter to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(slots):
                    target = slots[idx]
                    confirm = input(f"Delete '{target}'? (y/n): ").lower()
                    if confirm == 'y':
                        if state.delete_slot(target):
                            print("Chapter deleted.")
                        else:
                            print("Failed to delete.")
            except:
                print("Invalid selection.")
        
        elif cmd == "5": break

def _settings_menu(state: CanvasState):
    while True:
        print("\n--- Settings Management ---")
        print("1. App Settings (Global)")
        print("2. Story Settings (Importance Levels)")
        print("3. Attribute Templates")
        print("4. Back")
        cmd = input("Select: ").strip()
        
        if cmd == "1":
            print(f"\nEditing App Settings:")
            state.app_settings.llm_endpoint = input(f"LLM Endpoint (current: {state.app_settings.llm_endpoint}): ").strip() or state.app_settings.llm_endpoint
            state.app_settings.llm_model = input(f"LLM Model (current: {state.app_settings.llm_model}): ").strip() or state.app_settings.llm_model
            state.app_settings.snap_to_grid = input(f"Snap to Grid (current: {state.app_settings.snap_to_grid}) (y/n): ").lower() == 'y'
            state.app_settings.grid_size = int(input(f"Grid Size (current: {state.app_settings.grid_size}): ").strip() or state.app_settings.grid_size)
            save_app_settings(state.app_settings)
            print("App settings saved.")

        elif cmd == "2":
            print(f"\nImportance Levels: {', '.join(state.settings.importance_levels)}")
            print("1. Add Level\n2. Edit Level\n3. Remove Level\n4. Back")
            s_cmd = input("Select: ").strip()
            if s_cmd == "1":
                state.settings.importance_levels.append(input("New level name: ").strip())
            elif s_cmd == "2":
                for i, l in enumerate(state.settings.importance_levels): print(f"{i+1}. {l}")
                idx = int(input("Select index: ")) - 1
                state.settings.importance_levels[idx] = input("New name: ").strip()
            elif s_cmd == "3":
                for i, l in enumerate(state.settings.importance_levels): print(f"{i+1}. {l}")
                idx = int(input("Select index to remove: ")) - 1
                state.settings.importance_levels.pop(idx)
            state.save_settings(state.settings)

        elif cmd == "3":
            _attribute_template_menu(state)
        
        elif cmd == "4": break

def _attribute_template_menu(state: CanvasState):
    etype_map = {"1": "Actor", "2": "Place", "3": "Item", "4": "Knowledge", "5": "Event"}
    while True:
        print("\n--- Attribute Template Management ---")
        print("Select Entity Type: 1. Actor, 2. Place, 3. Item, 4. Knowledge, 5. Event, 6. Back")
        choice = input("Select: ").strip()
        if choice == "6": break
        etype = etype_map.get(choice)
        if not etype: continue
        
        templates = {
            "Actor": state.settings.actor_attributes,
            "Place": state.settings.place_attributes,
            "Item": state.settings.item_attributes,
            "Knowledge": state.settings.knowledge_attributes,
            "Event": state.settings.event_attributes
        }[etype]
        
        print(f"\n{etype} Templates:")
        for i, t in enumerate(templates):
            print(f"{i+1}. {t.name} ({t.attr_type}) {'[Req]' if t.required else ''}")
        
        print("\n1. Add Template\n2. Edit Template\n3. Remove Template\n4. Back")
        t_cmd = input("Select: ").strip()
        if t_cmd == "1":
            name = input("Name: ").strip()
            print("Type: 1. text, 2. number, 3. select")
            at_type = {"1": AttributeType.TEXT, "2": AttributeType.NUMBER, "3": AttributeType.SELECT}.get(input("Type: "), AttributeType.TEXT)
            req = input("Required? (y/n): ").lower() == 'y'
            opts = []
            if at_type == AttributeType.SELECT:
                opts = [s.strip() for s in input("Options (sep by ;): ").split(';')]
            templates.append(AttributeTemplate(name=name, attr_type=at_type, required=req, options=opts))
        elif t_cmd == "2":
            idx = int(input("Index: ")) - 1
            t = templates[idx]
            t.name = input(f"Name ({t.name}): ").strip() or t.name
            t.required = input(f"Required ({t.required}) (y/n): ").lower() == 'y'
            if t.attr_type == AttributeType.SELECT:
                t.options = [s.strip() for s in input(f"Options ({';'.join(t.options)}): ").split(';')] or t.options
        elif t_cmd == "3":
            templates.pop(int(input("Index: ")) - 1)
        
        state.save_settings(state.settings)

def _select_importance(state, current=None):
    print(f"\nImportance levels (current: {current or 'None'}):")
    for i, level in enumerate(state.settings.importance_levels):
        print(f"{i+1}. {level}")
    choice = input("Select (Enter for default): ").strip()
    try:
        idx = int(choice) - 1
        return state.settings.importance_levels[idx]
    except:
        return current or state.settings.importance_levels[-1]

def _get_all_linkable(state):
    items = []
    for uid, identity in state.registry.entities.items():
        if uid in state.entity_states:
            items.append({'uid': uid, 'name': identity.name, 'type': identity.entity_type})
    for ev in state.events:
        items.append({'uid': ev.uid, 'name': ev.name, 'type': 'Event'})
    return items

def _list_everything(state: CanvasState):
    entities = list_all_entities(state)
    uid_to_name = {e.uid: e.name for e in entities}
    list_all_events(state)
    print("\n--- Relationships ---")
    for r in state.relationships:
        src_name = uid_to_name.get(r.source_uid, r.source_uid[:8])
        dst_name = uid_to_name.get(r.target_uid, r.target_uid[:8])
        print(f"{src_name} --({r.rel_type.value}: {r.description})--> {dst_name}")

def _generator_cli(state: CanvasState):
    from .generators import generate_any
    import json
    print("\n--- Random Generator ---")
    types = ['Names', 'Traits', 'Character', 'Place', 'Item', 'Knowledge', 'Event']
    for i, t in enumerate(types): print(f"{i+1}. {t}")
    choice = input("\nSelect generator type (number): ").strip()
    try:
        t_idx = int(choice) - 1
        if 0 <= t_idx < len(types):
            gen_type = types[t_idx]
            count = int(input("Count (default 1): ").strip() or 1)
            prompt = input("Custom prompt (optional): ").strip()
            force_proc = input("Force procedural? (y/n): ").lower() == 'y'
            print(f"\nGenerating {gen_type}...")
            result = generate_any(gen_type, state.app_settings.llm_endpoint, state.app_settings.llm_model, count=count, custom_prompt=prompt, force_procedural=force_proc)
            if result:
                print("\nResult:", json.dumps(result, indent=2))
                if input("\nSave to Canvas? (y/n): ").lower() == 'y':
                    if gen_type == "Names":
                        for name in result.get('names', []): state.create_entity(name, "Actor", "extra", {})
                    elif gen_type == "Character":
                        state.create_entity(result['name'], "Actor", "secondary", {"Role": result['role'], "Personality": result['personality'], "Traits": ", ".join(result['traits'])})
                    elif gen_type in ["Place", "Item", "Knowledge"]:
                        state.create_entity(result['name'], gen_type, "extra", result.get('attributes', {}))
                    elif gen_type == "Event":
                        ev = Event(name=result['name'], description=result['description'], involved_uids=result.get('involved_uids', []), location_uid=result.get('location_uid'), x=result.get('x', 500), y=result.get('y', 500))
                        state.save_event(ev)
                    print(f"Saved {gen_type}.")
    except Exception as e: print(f"Error: {str(e)}")

def _edit_prose_cli(state: CanvasState):
    while True:
        print(f"\n--- Prose Editor [{state.current_slot}] ---")
        print(f"Title: {state.prose.title}")
        print(f"Content: {state.prose.content[:100]}..." if state.prose.content else "Content: (empty)")
        print("\n1. Edit Title\n2. Edit Content\n3. View Full\n4. Clear\n5. Back")
        choice = input("Select: ").strip()
        if choice == "1":
            state.prose.title = input("Enter new title: ").strip()
            state.save_prose(state.prose)
        elif choice == "2":
            print("Enter content (type END on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END": break
                lines.append(line)
            state.prose.content = "\n".join(lines)
            state.save_prose(state.prose)
        elif choice == "3":
            print(f"\n--- {state.prose.title} ---\n{state.prose.content}\n---")
        elif choice == "4":
            if input("Clear prose? (y/n): ").lower() == 'y':
                state.prose.title = ""; state.prose.content = ""
                state.save_prose(state.prose)
        elif choice == "5": break

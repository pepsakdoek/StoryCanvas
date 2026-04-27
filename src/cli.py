import os
import shutil
import uuid
from .storage import CanvasState, get_available_canvases, SAVES_DIR
from .models import Relationship, DefaultImportance, RelationshipType, EntityIdentity, EntityState

def get_next_canvas_name(base_name: str) -> str:
    canvases = get_available_canvases()
    # If base_name is "MyWorld", try "MyWorld_1", "MyWorld_2", etc.
    name = base_name.split('_')[0]
    i = 1
    while f"{name}_{i}" in canvases:
        i += 1
    return f"{name}_{i}"

def input_attributes(templates):
    attributes = {}
    if not templates:
        return attributes
    print("\nEnter attributes (leave empty to skip):")
    for template in templates:
        if not template.enabled:
            continue
        val = input(f"{template.name}: ").strip()
        if val:
            attributes[template.name] = val
    
    while True:
        attr_name = input("Custom attribute name (or Enter to finish): ").strip()
        if not attr_name:
            break
        attr_val = input(f"{attr_name} value: ").strip()
        if attr_val:
            attributes[attr_name] = attr_val
    return attributes

def list_all_entities(state: CanvasState):
    entities = []
    # Collect all identities from registry that have state in current slot
    idx = 1
    print("\n--- Entities ---")
    
    # Group by type for better display
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
            if identity.entity_type == 'Actor':
                info += f" ({identity.importance})"
            print(info)
            entities.append(identity)
            idx += 1
            
    return entities

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
        print(f"\n--- {canvas_name} [{state.current_slot}] Menu ---")
        print("1. Add Actor")
        print("2. Add Place")
        print("3. Add Item")
        print("4. Add Knowledge")
        print("5. Add Relationship")
        print("6. List Everything")
        print("7. Create New Chapter")
        print("8. Switch Chapter")
        print("9. Delete Entity")
        print("10. Delete Relationship")
        print("11. Delete Chapter")
        print("12. View/Edit Prose")
        print("13. Random Generator")
        print("14. Exit")
        cmd = input("Select action: ").strip()
        
        if cmd == "1":
            # ... (Existing logic)
            name = input("Enter actor name: ").strip()
            if not name: continue
            
            print("\nImportance levels:")
            for i, level in enumerate(state.settings.importance_levels):
                print(f"{i+1}. {level}")
            
            imp_choice = input(f"Select importance (1-{len(state.settings.importance_levels)}, default {len(state.settings.importance_levels)}): ").strip()
            importance = state.settings.importance_levels[-1]
            try:
                imp_idx = int(imp_choice) - 1
                if 0 <= imp_idx < len(state.settings.importance_levels):
                    importance = state.settings.importance_levels[imp_idx]
            except:
                pass
            
            attrs = input_attributes(state.settings.actor_attributes)
            state.create_entity(name, "Actor", importance, attrs)
        
        elif cmd in ["2", "3", "4"]:
            etype = {"2": "Place", "3": "Item", "4": "Knowledge"}[cmd]
            name = input(f"Enter {etype.lower()} name: ").strip()
            if not name: continue
            
            mapping = {"Place": state.settings.place_attributes, 
                       "Item": state.settings.item_attributes, 
                       "Knowledge": state.settings.knowledge_attributes}
            attrs = input_attributes(mapping[etype])
            state.create_entity(name, etype, DefaultImportance.EXTRA.value, attrs)

        elif cmd == "5":
            entities = list_all_entities(state)
            if len(entities) < 2:
                print("Need at least 2 entities to create a relationship.")
                continue
            
            try:
                src_idx = int(input("\nSelect source entity (number): ")) - 1
                dst_idx = int(input("Select target entity (number): ")) - 1
                
                print("\nRelationship Types: 1. agency, 2. causality, 3. sentiment, 4. chronotope")
                rel_choice = input("Select type (1-4): ").strip()
                rel_type = RelationshipType.SENTIMENT
                if rel_choice == "1": rel_type = RelationshipType.AGENCY
                elif rel_choice == "2": rel_type = RelationshipType.CAUSALITY
                elif rel_choice == "4": rel_type = RelationshipType.CHRONOTOPE
                
                description = input("Enter description: ").strip()
                
                rel = Relationship(
                    source_uid=entities[src_idx].uid,
                    target_uid=entities[dst_idx].uid,
                    rel_type=rel_type,
                    description=description
                )
                state.save_relationship(rel)
                print("Relationship added.")
            except (ValueError, IndexError):
                print("Invalid selection.")

        elif cmd == "6":
            entities = list_all_entities(state)
            uid_to_name = {e.uid: e.name for e in entities}
            print("\n--- Relationships ---")
            for r in state.relationships:
                src_name = uid_to_name.get(r.source_uid, r.source_uid[:8])
                dst_name = uid_to_name.get(r.target_uid, r.target_uid[:8])
                print(f"{src_name} --({r.rel_type.value}: {r.description})--> {dst_name}")

        elif cmd == "7":
            new_name = input("Enter name for new Chapter: ").strip()
            if new_name:
                if state.create_slot(new_name, clone_current=True):
                    print(f"Created and switched to chapter: {new_name}")
                else:
                    print("Chapter already exists or failed to create.")

        elif cmd == "8":
            slots = state.get_slots()
            print("\nAvailable Chapters:")
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

        elif cmd == "9":
            entities = list_all_entities(state)
            choice = input("Select entity to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(entities):
                    state.delete_entity(entities[idx].uid)
                    print("Entity deleted.")
            except:
                print("Invalid selection.")

        elif cmd == "10":
            print("\n--- Relationships ---")
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

        elif cmd == "11":
            slots = state.get_slots()
            if len(slots) <= 1:
                print("Cannot delete the only chapter.")
                continue
            
            print("\nAvailable Chapters:")
            for i, s in enumerate(slots):
                print(f"{i+1}. {s}")
            
            choice = input("Select chapter to delete (number): ").strip()
            try:
                idx = int(choice) - 1
                if 0 <= idx < len(slots):
                    target = slots[idx]
                    if target == state.current_slot:
                        print("Cannot delete current chapter. Switch first.")
                    else:
                        confirm = input(f"Are you sure you want to delete '{target}'? (y/n): ").lower()
                        if confirm == 'y':
                            shutil.rmtree(os.path.join(state.slots_dir, target))
                            print("Chapter deleted.")
            except:
                print("Invalid selection.")

        elif cmd == "12":
            _edit_prose_cli(state)

        elif cmd == "13":
            _generator_cli(state)

        elif cmd == "14":
            break

def _generator_cli(state: CanvasState):
    from .generators import generate_any
    from .models import Event
    import json

    print("\n--- Random Generator ---")
    types = ['Names', 'Traits', 'Character', 'Place', 'Item', 'Knowledge', 'Event']
    for i, t in enumerate(types):
        print(f"{i+1}. {t}")
    
    choice = input("\nSelect generator type (number): ").strip()
    try:
        t_idx = int(choice) - 1
        if 0 <= t_idx < len(types):
            gen_type = types[t_idx]
            count = 1
            if gen_type in ["Names", "Traits"]:
                count_str = input("Count (default 1): ").strip()
                if count_str: count = int(count_str)
            
            prompt = input("Custom prompt (optional): ").strip()
            
            force_proc = input("Force procedural? (y/n, default n): ").lower() == 'y'
            
            print(f"\nGenerating {gen_type}...")
            result = generate_any(
                gen_type,
                state.settings.llm_endpoint,
                state.settings.llm_model,
                count=count,
                custom_prompt=prompt,
                force_procedural=force_proc
            )
            
            if result:
                print("\nGenerated Result:")
                print(json.dumps(result, indent=2))
                
                save = input("\nSave to Canvas? (y/n): ").lower()
                if save == 'y':
                    if gen_type == "Names":
                        for name in result.get('names', []):
                            state.create_entity(name, "Actor", "extra", {})
                    elif gen_type == "Character":
                        state.create_entity(result['name'], "Actor", "secondary", 
                                            {"Role": result['role'], "Personality": result['personality'], 
                                             "Traits": ", ".join(result['traits'])})
                    elif gen_type in ["Place", "Item", "Knowledge"]:
                        state.create_entity(result['name'], gen_type, "extra", result.get('attributes', {}))
                    elif gen_type == "Event":
                        ev = Event(
                            name=result['name'],
                            description=result['description'],
                            involved_uids=result.get('involved_uids', []),
                            location_uid=result.get('location_uid'),
                            x=result.get('x', 500),
                            y=result.get('y', 500)
                        )
                        state.save_event(ev)
                    print(f"Saved {gen_type} to canvas.")
            else:
                print("Generation failed.")
    except Exception as e:
        print(f"Error: {str(e)}")

def _edit_prose_cli(state: CanvasState):
    print(f"\n--- Prose Editor [{state.current_slot}] ---")
    print(f"Title: {state.prose.title}")
    print("\nCurrent Content:")
    if state.prose.content:
        print(state.prose.content)
    else:
        print("(empty)")
    
    while True:
        print("\nOptions:")
        print("1. Edit Title")
        print("2. Edit Content")
        print("3. View Full Content")
        print("4. Clear All")
        print("5. Back")
        choice = input("Select: ").strip()
        
        if choice == "1":
            new_title = input("Enter new title: ").strip()
            state.prose.title = new_title
            state.save_prose(state.prose)
            print(f"Title updated to: {new_title}")
        
        elif choice == "2":
            print("Enter content (type END on a new line to finish):")
            lines = []
            while True:
                line = input()
                if line.strip() == "END":
                    break
                lines.append(line)
            new_content = "\n".join(lines)
            state.prose.content = new_content
            state.save_prose(state.prose)
            print("Content updated!")
        
        elif choice == "3":
            print("\n--- Full Prose Content ---")
            print(state.prose.content if state.prose.content else "(empty)")
            print("--- End ---\n")
        
        elif choice == "4":
            confirm = input("Clear all prose content? (y/n): ").lower()
            if confirm == 'y':
                state.prose.title = ""
                state.prose.content = ""
                state.save_prose(state.prose)
                print("Prose cleared!")
        
        elif choice == "5":
            break

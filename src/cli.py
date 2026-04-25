import os
import shutil
from .storage import CanvasState, get_available_canvases, SAVES_DIR
from .models import Actor, Place, Item, Knowledge, Relationship, Importance, RelationshipType, Entity

def get_next_canvas_name(base_name: str) -> str:
    canvases = get_available_canvases()
    if base_name not in canvases:
        return base_name
    
    i = 1
    while f"{base_name}_{i}" in canvases:
        i += 1
    return f"{base_name}_{i}"

def input_attributes(templates, state_config):
    attributes = {}
    print("\nEnter attributes (leave name empty to stop):")
    for template in templates:
        val = input(f"{template.name}: ").strip()
        if val:
            attributes[template.name] = val
    
    while True:
        attr_name = input("Custom attribute name: ").strip()
        if not attr_name:
            break
        attr_val = input(f"{attr_name} value: ").strip()
        if attr_val:
            attributes[attr_name] = attr_val
    return attributes

def list_all_entities(state: CanvasState):
    entities = []
    idx = 1
    print("\n--- Actors ---")
    for e in state.actors:
        print(f"{idx}. [{e.uid[:8]}] {e.name} (Actor, {e.importance.value})")
        entities.append(e)
        idx += 1
    print("\n--- Places ---")
    for e in state.places:
        print(f"{idx}. [{e.uid[:8]}] {e.name} (Place)")
        entities.append(e)
        idx += 1
    print("\n--- Items ---")
    for e in state.items:
        print(f"{idx}. [{e.uid[:8]}] {e.name} (Item)")
        entities.append(e)
        idx += 1
    print("\n--- Knowledge ---")
    for e in state.knowledge:
        print(f"{idx}. [{e.uid[:8]}] {e.name} (Knowledge)")
        entities.append(e)
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
        print(f"\n--- {canvas_name} Menu ---")
        print("1. Add Actor")
        print("2. Add Place")
        print("3. Add Item")
        print("4. Add Knowledge")
        print("5. Add Relationship")
        print("6. List Everything")
        print("7. Create New Version (Numbered Save)")
        print("8. Delete this Canvas and Restart")
        print("9. Exit")
        cmd = input("Select action: ").strip()
        
        if cmd == "1":
            name = input("Enter actor name: ").strip()
            if not name: continue
            print("\nImportance levels: 1. main, 2. secondary, 3. tertiary, 4. extra")
            imp_choice = input("Select importance (1-4, default 4): ").strip()
            importance = Importance.EXTRA
            if imp_choice == "1": importance = Importance.MAIN
            elif imp_choice == "2": importance = Importance.SECONDARY
            elif imp_choice == "3": importance = Importance.TERTIARY
            
            attrs = input_attributes(state.config.actor_attributes, state.config)
            state.save_entity(Actor(name=name, importance=importance, attributes=attrs))
        
        elif cmd == "2":
            name = input("Enter place name: ").strip()
            if not name: continue
            attrs = input_attributes(state.config.place_attributes, state.config)
            state.save_entity(Place(name=name, attributes=attrs))

        elif cmd == "3":
            name = input("Enter item name: ").strip()
            if not name: continue
            attrs = input_attributes(state.config.item_attributes, state.config)
            state.save_entity(Item(name=name, attributes=attrs))

        elif cmd == "4":
            name = input("Enter knowledge/fact: ").strip()
            if not name: continue
            attrs = input_attributes(state.config.knowledge_attributes, state.config)
            state.save_entity(Knowledge(name=name, attributes=attrs))

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
            new_name = get_next_canvas_name(canvas_name.split('_')[0])
            new_path = os.path.join(SAVES_DIR, new_name)
            shutil.copytree(state.path, new_path)
            print(f"Cloned current canvas to {new_name}")
            state = CanvasState(new_name)
            canvas_name = new_name

        elif cmd == "8":
            confirm = input(f"Are you sure you want to DELETE {canvas_name}? (y/n): ").lower()
            if confirm == 'y':
                shutil.rmtree(state.path)
                print("Canvas deleted.")
                return 

        elif cmd == "9":
            break

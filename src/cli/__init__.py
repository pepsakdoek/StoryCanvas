import os
import json
from ..storage import CanvasState, get_available_canvases
from ..models import Event
from .utils import list_all_entities, list_all_events
from .entities import entity_menu, event_menu
from .relationships import relationship_menu
from .chapters import chapter_menu
from .settings import settings_menu

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
        
        if cmd == "1": entity_menu(state)
        elif cmd == "2": event_menu(state)
        elif cmd == "3": relationship_menu(state)
        elif cmd == "4": chapter_menu(state)
        elif cmd == "5": _edit_prose_cli(state)
        elif cmd == "6": _generator_cli(state)
        elif cmd == "7": settings_menu(state)
        elif cmd == "8":
            state.auto_arrange()
            print("Canvas auto-arranged.")
        elif cmd == "9": _list_everything(state)
        elif cmd == "0": break

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
    from ..generators import generate_any
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
                save = input("\nSave to Canvas? (y/n): ").lower()
                if save == 'y':
                    source = result.get('generation_source', 'manual')
                    if gen_type == "Names":
                        for name in result.get('names', []): 
                            state.create_entity(name, "Actor", "extra", {"Generation Source": source})
                    elif gen_type == "Character":
                        attrs = {
                            "Role": result['role'], 
                            "Personality": result['personality'], 
                            "Traits": ", ".join(result['traits']),
                            "Generation Source": source
                        }
                        state.create_entity(result['name'], "Actor", "secondary", attrs)
                    elif gen_type in ["Place", "Item", "Knowledge"]:
                        attrs = result.get('attributes', {}).copy()
                        attrs["Generation Source"] = source
                        state.create_entity(result['name'], gen_type, "extra", attrs)
                    elif gen_type == "Event":
                        attrs = result.get('attributes', {}).copy()
                        attrs["Generation Source"] = source
                        ev = Event(
                            name=result['name'], 
                            description=result['description'], 
                            involved_uids=result.get('involved_uids', []), 
                            location_uid=result.get('location_uid'), 
                            attributes=attrs,
                            x=result.get('x', 500), 
                            y=result.get('y', 500)
                        )
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

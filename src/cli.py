from .storage import CanvasState, get_available_canvases
from .models import Actor, Importance

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
        print("\n1. Add Actor")
        print("2. List Actors")
        print("3. Exit")
        cmd = input("Select action: ").strip()
        
        if cmd == "1":
            name = input("Enter actor name: ").strip()
            if not name:
                print("Error: Name is required.")
                continue
            
            print("\nImportance levels:")
            for i, level in enumerate(Importance):
                print(f"{i+1}. {level.value}")
            imp_choice = input("Select importance (number, default 4): ").strip()
            importance = Importance.EXTRA
            try:
                imp_idx = int(imp_choice) - 1
                importance = list(Importance)[imp_idx]
            except:
                pass

            attributes = {}
            print("\nEnter attributes (leave name empty to stop):")
            # First suggest from config
            for template in state.config.actor_attributes:
                val = input(f"{template.name}: ").strip()
                if val:
                    attributes[template.name] = val
            
            # Then allow custom
            while True:
                attr_name = input("Custom attribute name: ").strip()
                if not attr_name:
                    break
                attr_val = input(f"{attr_name} value: ").strip()
                if attr_val:
                    attributes[attr_name] = attr_val

            actor = Actor(name=name, importance=importance, attributes=attributes)
            state.save_actor(actor)
            print(f"Added: {name}")
        elif cmd == "2":
            for a in state.actors:
                attr_str = ", ".join([f"{k}: {v}" for k, v in a.attributes.items()])
                print(f"- {a.name} [{a.importance.value}]: {attr_str} ({a.uid})")
        elif cmd == "3":
            break

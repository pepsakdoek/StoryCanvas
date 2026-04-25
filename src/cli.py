from .storage import CanvasState, get_available_canvases
from .models import Actor

def run_cli():
    print("--- Bard CLI ---")
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
            description = input("Enter actor description: ").strip()
            actor = Actor(name=name, description=description)
            state.save_actor(actor)
            print(f"Added: {name}")
        elif cmd == "2":
            for a in state.actors:
                print(f"- {a.name}: {a.description} ({a.uid})")
        elif cmd == "3":
            break

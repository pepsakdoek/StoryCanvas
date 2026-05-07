def chapter_menu(state):
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

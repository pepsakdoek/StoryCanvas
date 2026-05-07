from ..storage import save_app_settings
from ..models import AttributeType, AttributeTemplate

def settings_menu(state):
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
                try:
                    idx = int(input("Select index: ")) - 1
                    state.settings.importance_levels[idx] = input("New name: ").strip()
                except: print("Invalid selection.")
            elif s_cmd == "3":
                for i, l in enumerate(state.settings.importance_levels): print(f"{i+1}. {l}")
                try:
                    idx = int(input("Select index to remove: ")) - 1
                    state.settings.importance_levels.pop(idx)
                except: print("Invalid selection.")
            state.save_settings(state.settings)

        elif cmd == "3":
            _attribute_template_menu(state)
        
        elif cmd == "4": break

def _attribute_template_menu(state):
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
            try:
                idx = int(input("Index: ")) - 1
                t = templates[idx]
                t.name = input(f"Name ({t.name}): ").strip() or t.name
                t.required = input(f"Required ({t.required}) (y/n): ").lower() == 'y'
                if t.attr_type == AttributeType.SELECT:
                    new_opts = input(f"Options ({';'.join(t.options)}): ").strip()
                    if new_opts:
                        t.options = [s.strip() for s in new_opts.split(';')]
            except: print("Invalid selection.")
        elif t_cmd == "3":
            try:
                templates.pop(int(input("Index: ")) - 1)
            except: print("Invalid selection.")
        
        state.save_settings(state.settings)

import json
from ..models import AttributeType, AttributeTemplate

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
        custom_attrs = [f"{k}={v}" for k,v in attributes.items() if k not in [t.name for t in templates]]
        print("\nCustom attributes (currently: " + ", ".join(custom_attrs) + ")")
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

def _select_importance(state, current=None):
    print(f"\nImportance levels (current: {current or 'None'}):")
    for i, level in enumerate(state.settings.importance_levels):
        print(f"{i+1}. {level}")
    choice = input("Select (Enter for default): ").strip()
    try:
        idx = int(choice) - 1
        if 0 <= idx < len(state.settings.importance_levels):
            return state.settings.importance_levels[idx]
        return current or state.settings.importance_levels[-1]
    except:
        return current or state.settings.importance_levels[-1]

def list_all_entities(state):
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

def list_all_events(state):
    print("\n--- Events ---")
    for i, ev in enumerate(state.events):
        print(f"{i+1}. [{ev.uid[:8]}] {ev.name} (Imp: {ev.importance}, Pos: {ev.x}, {ev.y})")
    return state.events

def _get_all_linkable(state):
    items = []
    for uid, identity in state.registry.entities.items():
        if uid in state.entity_states:
            items.append({'uid': uid, 'name': identity.name, 'type': identity.entity_type})
    for ev in state.events:
        items.append({'uid': ev.uid, 'name': ev.name, 'type': 'Event'})
    return items

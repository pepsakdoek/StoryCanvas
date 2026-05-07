from ..models import Relationship, RelationshipType
from .utils import _get_all_linkable

def relationship_menu(state):
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

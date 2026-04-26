import os
import json
import shutil
from typing import List, Dict, Type, TypeVar, Any, Optional
from .models import EntityIdentity, GlobalRegistry, EntityState, Event, Relationship, CanvasSettings

SAVES_DIR = "save"
os.makedirs(SAVES_DIR, exist_ok=True)

class CanvasState:
    def __init__(self, canvas_name: str, slot_name: str = "Chapter 1"):
        self.canvas_name = canvas_name
        self.canvas_path = os.path.join(SAVES_DIR, canvas_name)
        os.makedirs(self.canvas_path, exist_ok=True)
        
        # 1. Root data (Global)
        self.settings_file = os.path.join(self.canvas_path, "settings.json")
        self.registry_file = os.path.join(self.canvas_path, "registry.json")
        self.settings = self.load_settings()
        self.registry = self.load_registry()
        
        self.slots_dir = os.path.join(self.canvas_path, "slots")
        os.makedirs(self.slots_dir, exist_ok=True)
        
        # 2. Temporal data (Slot-specific)
        if not self.get_slots():
            self.current_slot = slot_name
            self._init_slot(self.current_slot)
        else:
            self.current_slot = slot_name if slot_name in self.get_slots() else self.get_slots()[0]
            
        self._load_current_slot()

    def load_registry(self) -> GlobalRegistry:
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r") as f:
                try: return GlobalRegistry(**json.load(f))
                except: return GlobalRegistry()
        return GlobalRegistry()

    def save_registry(self):
        with open(self.registry_file, "w") as f:
            json.dump(self.registry.model_dump(), f, indent=4)

    def _init_slot(self, name: str):
        path = os.path.join(self.slots_dir, name)
        os.makedirs(path, exist_ok=True)

    def _load_current_slot(self):
        self.slot_path = os.path.join(self.slots_dir, self.current_slot)
        self.states_file = os.path.join(self.slot_path, "States.json")
        self.events_file = os.path.join(self.slot_path, "Events.json")
        self.relationships_file = os.path.join(self.slot_path, "Relationships.json")
        
        self.entity_states: Dict[str, EntityState] = self._load_states()
        self.events: List[Event] = self._load_events()
        self.relationships: List[Relationship] = self._load_relationships()

    def get_slots(self) -> List[str]:
        if not os.path.exists(self.slots_dir): return []
        return sorted([d for d in os.listdir(self.slots_dir) if os.path.isdir(os.path.join(self.slots_dir, d))])

    def switch_slot(self, name: str):
        if name in self.get_slots():
            self.current_slot = name
            self._load_current_slot()

    def create_slot(self, name: str, clone_current: bool = True):
        new_path = os.path.join(self.slots_dir, name)
        if os.path.exists(new_path): return False
        if clone_current and os.path.exists(self.slot_path):
            shutil.copytree(self.slot_path, new_path)
        else:
            os.makedirs(new_path, exist_ok=True)
        self.current_slot = name
        self._load_current_slot()
        return True

    def create_entity(self, name: str, entity_type: str, importance: str, attributes: Dict[str, str]):
        import uuid
        uid = str(uuid.uuid4())
        # Global Identity
        identity = EntityIdentity(uid=uid, name=name, entity_type=entity_type, importance=importance)
        self.registry.entities[uid] = identity
        self.save_registry()
        
        # Initial State
        state = EntityState(uid=uid, attributes=attributes)
        self.entity_states[uid] = state
        self.save_states()
        return uid

    def update_identity(self, uid: str, name: str, importance: str):
        if uid in self.registry.entities:
            self.registry.entities[uid].name = name
            self.registry.entities[uid].importance = importance
            self.save_registry()

    def update_state(self, uid: str, x: float, y: float, attributes: Dict[str, str]):
        state = self.entity_states.get(uid, EntityState(uid=uid))
        state.x, state.y = x, y
        state.attributes = attributes
        self.entity_states[uid] = state
        self.save_states()

    def _load_states(self) -> Dict[str, EntityState]:
        if os.path.exists(self.states_file):
            with open(self.states_file, "r") as f:
                try: 
                    data = json.load(f)
                    return {s['uid']: EntityState(**s) for s in data}
                except: return {}
        return {}

    def save_states(self):
        with open(self.states_file, "w") as f:
            json.dump([s.model_dump() for s in self.entity_states.values()], f, indent=4)

    def _load_events(self) -> List[Event]:
        if os.path.exists(self.events_file):
            with open(self.events_file, "r") as f:
                try: 
                    data = json.load(f)
                    return [Event(**e) for e in data]
                except: return []
        return []

    def save_event(self, event: Event):
        # find and replace or append
        for i, e in enumerate(self.events):
            if e.uid == event.uid:
                self.events[i] = event
                break
        else:
            self.events.append(event)
        
        with open(self.events_file, "w") as f:
            json.dump([e.model_dump() for e in self.events], f, indent=4)

    def load_settings(self) -> CanvasSettings:
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                try: return CanvasSettings(**json.load(f))
                except: return CanvasSettings()
        settings = CanvasSettings()
        self.save_settings(settings)
        return settings

    def save_settings(self, settings: CanvasSettings):
        with open(self.settings_file, "w") as f:
            json.dump(settings.model_dump(), f, indent=4)

    def _load_relationships(self) -> List[Relationship]:
        if os.path.exists(self.relationships_file):
            with open(self.relationships_file, "r") as f:
                try: 
                    data = json.load(f)
                    return [Relationship(**r) for r in data]
                except: return []
        return []

    def save_relationship(self, rel: Relationship):
        for i, existing in enumerate(self.relationships):
            if existing.uid == rel.uid:
                self.relationships[i] = rel
                break
        else:
            self.relationships.append(rel)
        self.save_relationships()

    def save_relationships(self):
        with open(self.relationships_file, "w") as f:
            json.dump([r.model_dump() for r in self.relationships], f, indent=4)

    def delete_entity(self, uid: str):
        # We can remove state from current slot
        if uid in self.entity_states:
            del self.entity_states[uid]
            self.save_states()
        # Should we delete from registry? Only if not used in ANY slot.
        # For simplicity, let's keep it in registry but remove from current slot's "active" list
        self.relationships = [r for r in self.relationships if r.source_uid != uid and r.target_uid != uid]
        with open(self.relationships_file, "w") as f:
            json.dump([r.model_dump() for r in self.relationships], f, indent=4)

def get_available_canvases():
    if not os.path.exists(SAVES_DIR): return []
    return sorted([d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))])

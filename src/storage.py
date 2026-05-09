import os
import json
import shutil
from typing import List, Dict, Type, TypeVar, Any, Optional
from .models import EntityIdentity, GlobalRegistry, EntityState, Event, Relationship, CanvasSettings, Prose, Beat, AppSettings

SAVES_DIR = "save"
os.makedirs(SAVES_DIR, exist_ok=True)
APP_SETTINGS_FILE = os.path.join(SAVES_DIR, "app_settings.json")

def load_app_settings() -> AppSettings:
    if os.path.exists(APP_SETTINGS_FILE):
        with open(APP_SETTINGS_FILE, "r") as f:
            try: return AppSettings(**json.load(f))
            except: return AppSettings()
    return AppSettings()

def save_app_settings(settings: AppSettings):
    with open(APP_SETTINGS_FILE, "w") as f:
        json.dump(settings.model_dump(), f, indent=4)

class CanvasState:
    def __init__(self, canvas_name: str):
        self.canvas_name = canvas_name
        self.canvas_path = os.path.join(SAVES_DIR, canvas_name)
        os.makedirs(self.canvas_path, exist_ok=True)
        
        self.app_settings = load_app_settings()
        self.settings_file = os.path.join(self.canvas_path, "settings.json")
        self.registry_file = os.path.join(self.canvas_path, "registry.json")
        self.settings = self.load_settings()
        self.registry = self.load_registry()
        
        self.slots_dir = os.path.join(self.canvas_path, "slots")
        os.makedirs(self.slots_dir, exist_ok=True)
        
        # Current Temporal Focus
        self.current_slot = self.get_slots()[0] if self.get_slots() else "Chapter 1"
        self.active_beat_idx = 0
        
        self._load_current_slot()
        self._sync_to_active_beat()

    def _load_current_slot(self):
        self.slot_path = os.path.join(self.slots_dir, self.current_slot)
        os.makedirs(self.slot_path, exist_ok=True)
        
        # Legacy File Paths (for migration)
        self.states_file = os.path.join(self.slot_path, "States.json")
        self.events_file = os.path.join(self.slot_path, "Events.json")
        self.relationships_file = os.path.join(self.slot_path, "Relationships.json")
        self.prose_file = os.path.join(self.slot_path, "Prose.json")
        
        self.prose: Prose = self._load_prose_and_migrate()

    def _load_prose_and_migrate(self) -> Prose:
        prose = Prose()
        if os.path.exists(self.prose_file):
            with open(self.prose_file, "r") as f:
                try: 
                    data = json.load(f)
                    # Legacy string migration
                    if 'content' in data and data['content'] and (not data.get('beats')):
                        paragraphs = [p.strip() for p in data['content'].split('\n\n') if p.strip()]
                        data['beats'] = [{'text': p} for p in paragraphs]
                        data['content'] = None
                    prose = Prose(**data)
                except: prose = Prose()

        if not prose.beats:
            prose.beats = [Beat(text="Once upon a time...")]

        # CRITICAL: If the first beat has no state, pull from legacy Chapter-level files
        if not prose.beats[0].entity_states:
            prose.beats[0].entity_states = self._load_legacy_dict(self.states_file, EntityState)
            prose.beats[0].events = self._load_legacy_list(self.events_file, Event)
            prose.beats[0].relationships = self._load_legacy_list(self.relationships_file, Relationship)
            self.save_prose(prose)
            
        return prose

    def _load_legacy_dict(self, path, model):
        if not os.path.exists(path): return {}
        try:
            with open(path, "r") as f:
                return {s['uid']: model(**s) for s in json.load(f)}
        except: return {}

    def _load_legacy_list(self, path, model):
        if not os.path.exists(path): return []
        try:
            with open(path, "r") as f:
                return [model(**i) for i in json.load(f)]
        except: return []

    def _sync_to_active_beat(self):
        """Points active data pointers to the focused beat's state."""
        if 0 <= self.active_beat_idx < len(self.prose.beats):
            beat = self.prose.beats[self.active_beat_idx]
            self.entity_states = beat.entity_states
            self.events = beat.events
            self.relationships = beat.relationships
        else:
            self.active_beat_idx = 0
            self._sync_to_active_beat()

    def set_active_beat(self, index: int):
        self.active_beat_idx = index
        self._sync_to_active_beat()

    def create_next_beat(self, after_idx: int, text: str = "") -> int:
        """Creates a new beat that inherits the state of the previous one."""
        current_beat = self.prose.beats[after_idx]
        new_states = {uid: EntityState(**s.model_dump()) for uid, s in current_beat.entity_states.items()}
        new_rels = [Relationship(**r.model_dump()) for r in current_beat.relationships]
        
        new_beat = Beat(text=text, entity_states=new_states, relationships=new_rels)
        self.prose.beats.insert(after_idx + 1, new_beat)
        self.save_prose(self.prose)
        return after_idx + 1

    def save_prose(self, prose: Prose):
        self.invalidate_timeline_cache()
        self.prose = prose
        with open(self.prose_file, "w") as f:
            json.dump(prose.model_dump(), f, indent=4)

    def save_registry(self):
        with open(self.registry_file, "w") as f:
            json.dump(self.registry.model_dump(), f, indent=4)

    def load_registry(self) -> GlobalRegistry:
        if os.path.exists(self.registry_file):
            with open(self.registry_file, "r") as f:
                try: return GlobalRegistry(**json.load(f))
                except: return GlobalRegistry()
        return GlobalRegistry()

    def load_settings(self) -> CanvasSettings:
        if os.path.exists(self.settings_file):
            with open(self.settings_file, "r") as f:
                try: return CanvasSettings(**json.load(f))
                except: return CanvasSettings()
        return CanvasSettings()

    def save_settings(self, settings: CanvasSettings):
        with open(self.settings_file, "w") as f:
            json.dump(settings.model_dump(), f, indent=4)

    def get_slots(self) -> List[str]:
        if not os.path.exists(self.slots_dir): return []
        return sorted([d for d in os.listdir(self.slots_dir) if os.path.isdir(os.path.join(self.slots_dir, d))])

    def switch_slot(self, name: str):
        if name in self.get_slots():
            self.current_slot = name
            self.active_beat_idx = 0
            self._load_current_slot()
            self._sync_to_active_beat()

    def create_slot(self, name: str, clone_current: bool = True):
        self.invalidate_timeline_cache()
        new_path = os.path.join(self.slots_dir, name)
        if os.path.exists(new_path): return False
        if clone_current and os.path.exists(self.slot_path):
            shutil.copytree(self.slot_path, new_path)
        else:
            os.makedirs(new_path, exist_ok=True)
        self.current_slot = name
        self._load_current_slot()
        return True

    def delete_slot(self, name: str):
        self.invalidate_timeline_cache()
        if name not in self.get_slots(): return False
        if len(self.get_slots()) <= 1: return False
        shutil.rmtree(os.path.join(self.slots_dir, name))
        if self.current_slot == name:
            self.current_slot = self.get_slots()[0]
            self._load_current_slot()
        return True

    def create_entity(self, name: str, entity_type: str, importance: str, attributes: Dict[str, str]):
        uid = str(uuid.uuid4())
        identity = EntityIdentity(uid=uid, name=name, entity_type=entity_type, importance=importance)
        self.registry.entities[uid] = identity
        self.save_registry()
        
        # Add to current beat's state
        state = EntityState(uid=uid, attributes=attributes)
        self.entity_states[uid] = state
        self.auto_arrange()
        self.save_prose(self.prose)
        return uid

    def update_identity(self, uid: str, name: str, importance: str):
        if uid in self.registry.entities:
            self.registry.entities[uid].name = name
            self.registry.entities[uid].importance = importance
            self.save_registry()

    def update_state(self, uid: str, x: float, y: float, attributes: Dict[str, str]):
        if uid not in self.entity_states:
            self.entity_states[uid] = EntityState(uid=uid)
        self.entity_states[uid].x, self.entity_states[uid].y = x, y
        self.entity_states[uid].attributes = attributes
        self.save_prose(self.prose)

    def save_event(self, event: Event):
        for i, e in enumerate(self.events):
            if e.uid == event.uid:
                self.events[i] = event
                break
        else:
            self.events.append(event)
        self.save_prose(self.prose)

    def save_relationship(self, rel: Relationship):
        for i, existing in enumerate(self.relationships):
            if existing.uid == rel.uid:
                self.relationships[i] = rel
                break
        else:
            self.relationships.append(rel)
        self.save_prose(self.prose)

    def delete_entity(self, uid: str):
        if uid in self.entity_states:
            del self.entity_states[uid]
        self.relationships = [r for r in self.relationships if r.source_uid != uid and r.target_uid != uid]
        self.save_prose(self.prose)

    def auto_arrange(self):
        sorted_uids = sorted(self.entity_states.keys())
        # (Same logic as before, just uses self.entity_states which is now beat-synced)
        places = [u for u in sorted_uids if self.registry.entities[u].entity_type == "Place"]
        for i, u in enumerate(places):
            self.entity_states[u].x, self.entity_states[u].y = 300 + (i%3)*500, 400 + (i//3)*400
        actors = [u for u in sorted_uids if self.registry.entities[u].entity_type == "Actor"]
        for i, u in enumerate(actors):
            self.entity_states[u].x, self.entity_states[u].y = 100 + (i%5)*300, 120 + (i//5)*240

    def get_timeline_map(self) -> Dict[str, Any]:
        if hasattr(self, '_timeline_cache') and self._timeline_cache:
            return self._timeline_cache
        mapping = []
        chapter_starts = {}
        total_beats = 0
        slots = self.get_slots()
        for slot in slots:
            chapter_starts[total_beats] = slot
            prose_path = os.path.join(self.slots_dir, slot, "Prose.json")
            beat_count = 0
            if os.path.exists(prose_path):
                try:
                    with open(prose_path, "r") as f:
                        data = json.load(f)
                        beat_count = len(data.get('beats', []))
                except: beat_count = 0
            for i in range(max(1, beat_count)):
                mapping.append({"slot": slot, "beat_idx": i})
            total_beats += max(1, beat_count)
        self._timeline_cache = {"mapping": mapping, "chapter_starts": chapter_starts, "total_beats": len(mapping)}
        return self._timeline_cache

    def invalidate_timeline_cache(self):
        self._timeline_cache = None

def get_available_canvases():
    if not os.path.exists(SAVES_DIR): return []
    return sorted([d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))])

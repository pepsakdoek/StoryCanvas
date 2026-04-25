import os
import json
from typing import List, Dict, Type, TypeVar, Any, Optional
from .models import Actor, Place, Item, Knowledge, Relationship, CanvasConfig, Entity

SAVES_DIR = "save"
os.makedirs(SAVES_DIR, exist_ok=True)

T = TypeVar('T', bound=Entity)

class CanvasState:
    def __init__(self, name: str):
        self.name = name
        self.path = os.path.join(SAVES_DIR, name)
        os.makedirs(self.path, exist_ok=True)
        
        self.config_file = os.path.join(self.path, "Config.json")
        self.actors_file = os.path.join(self.path, "Actors.json")
        self.places_file = os.path.join(self.path, "Places.json")
        self.items_file = os.path.join(self.path, "Items.json")
        self.knowledge_file = os.path.join(self.path, "Knowledge.json")
        self.relationships_file = os.path.join(self.path, "Relationships.json")
        
        self.config = self.load_config()
        self.actors: List[Actor] = self._load_entities(self.actors_file, Actor)
        self.places: List[Place] = self._load_entities(self.places_file, Place)
        self.items: List[Item] = self._load_entities(self.items_file, Item)
        self.knowledge: List[Knowledge] = self._load_entities(self.knowledge_file, Knowledge)
        self.relationships: List[Relationship] = self._load_relationships()

    def load_config(self) -> CanvasConfig:
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                try:
                    return CanvasConfig(**json.load(f))
                except:
                    return CanvasConfig()
        config = CanvasConfig()
        self.save_config(config)
        return config

    def save_config(self, config: CanvasConfig):
        with open(self.config_file, "w") as f:
            json.dump(config.model_dump(), f, indent=4)

    def _load_entities(self, file_path: str, model_class: Type[T]) -> List[T]:
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try:
                    data = json.load(f)
                    return [model_class(**a) for a in data]
                except (json.JSONDecodeError, TypeError):
                    return []
        return []

    def _load_relationships(self) -> List[Relationship]:
        if os.path.exists(self.relationships_file):
            with open(self.relationships_file, "r") as f:
                try:
                    data = json.load(f)
                    return [Relationship(**r) for r in data]
                except (json.JSONDecodeError, TypeError):
                    return []
        return []

    def _find_and_replace(self, collection: List[T], entity: T) -> bool:
        for i, existing in enumerate(collection):
            if existing.uid == entity.uid:
                collection[i] = entity
                return True
        collection.append(entity)
        return False

    def save_entity(self, entity: Entity):
        if isinstance(entity, Actor):
            self._find_and_replace(self.actors, entity)
            self._persist_entities(self.actors_file, self.actors)
        elif isinstance(entity, Place):
            self._find_and_replace(self.places, entity)
            self._persist_entities(self.places_file, self.places)
        elif isinstance(entity, Item):
            self._find_and_replace(self.items, entity)
            self._persist_entities(self.items_file, self.items)
        elif isinstance(entity, Knowledge):
            self._find_and_replace(self.knowledge, entity)
            self._persist_entities(self.knowledge_file, self.knowledge)

    def save_relationship(self, rel: Relationship):
        # Relationship updates are less common but let's be consistent
        for i, existing in enumerate(self.relationships):
            if existing.uid == rel.uid:
                self.relationships[i] = rel
                break
        else:
            self.relationships.append(rel)
        self._persist_relationships()

    def _persist_entities(self, file_path: str, entities: List[Entity]):
        with open(file_path, "w") as f:
            json.dump([e.model_dump() for e in entities], f, indent=4)

    def _persist_relationships(self):
        with open(self.relationships_file, "w") as f:
            json.dump([r.model_dump() for r in self.relationships], f, indent=4)

def get_available_canvases():
    if not os.path.exists(SAVES_DIR):
        return []
    return sorted([d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))])

import os
import json
from typing import List
from .models import Actor, CanvasConfig

SAVES_DIR = "save"
os.makedirs(SAVES_DIR, exist_ok=True)

class CanvasState:
    def __init__(self, name: str):
        self.name = name
        self.path = os.path.join(SAVES_DIR, name)
        self.actors_file = os.path.join(self.path, "Actors.json")
        self.config_file = os.path.join(self.path, "Config.json")
        os.makedirs(self.path, exist_ok=True)
        self.config = self.load_config()
        self.actors: List[Actor] = self.load_actors()

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

    def load_actors(self) -> List[Actor]:
        if os.path.exists(self.actors_file):
            with open(self.actors_file, "r") as f:
                try:
                    data = json.load(f)
                    return [Actor(**a) for a in data]
                except (json.JSONDecodeError, TypeError):
                    return []
        return []

    def save_actor(self, actor: Actor):
        self.actors.append(actor)
        self._persist()

    def update_actor(self, updated_actor: Actor):
        for i, actor in enumerate(self.actors):
            if actor.uid == updated_actor.uid:
                self.actors[i] = updated_actor
                break
        self._persist()

    def _persist(self):
        with open(self.actors_file, "w") as f:
            json.dump([a.model_dump() for a in self.actors], f, indent=4)

def get_available_canvases():
    if not os.path.exists(SAVES_DIR):
        return []
    return [d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))]

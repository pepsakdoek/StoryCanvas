import os
import json
from typing import List
from .models import Actor

SAVES_DIR = "save"
os.makedirs(SAVES_DIR, exist_ok=True)

class CanvasState:
    def __init__(self, name: str):
        self.name = name
        self.path = os.path.join(SAVES_DIR, name)
        self.actors_file = os.path.join(self.path, "Actors.json")
        os.makedirs(self.path, exist_ok=True)
        self.actors: List[Actor] = self.load_actors()

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
        with open(self.actors_file, "w") as f:
            json.dump([a.model_dump() for a in self.actors], f, indent=4)

def get_available_canvases():
    if not os.path.exists(SAVES_DIR):
        return []
    return [d for d in os.listdir(SAVES_DIR) if os.path.isdir(os.path.join(SAVES_DIR, d))]

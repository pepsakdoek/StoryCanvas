from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class Importance(str, Enum):
    MAIN = "main"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    EXTRA = "extra"

class AttributeTemplate(BaseModel):
    name: str
    description: str = ""
    required: bool = False

class CanvasConfig(BaseModel):
    # Recommended attributes for actors in this canvas
    actor_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Personality"),
        AttributeTemplate(name="Likes"),
        AttributeTemplate(name="Dislikes"),
        AttributeTemplate(name="Secret"),
        AttributeTemplate(name="Weakness"),
    ]

class Actor(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    importance: Importance = Importance.EXTRA
    # Flexible attributes: { "Attribute Name": "Value" }
    attributes: Dict[str, str] = Field(default_factory=dict)
    x: float = 100.0
    y: float = 100.0

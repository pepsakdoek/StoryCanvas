from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

# We'll keep the Enum as a default/fallback, but allow dynamic strings
class DefaultImportance(str, Enum):
    MAIN = "main"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    EXTRA = "extra"

class AttributeTemplate(BaseModel):
    name: str
    description: str = ""
    required: bool = False
    enabled: bool = True

class CanvasSettings(BaseModel):
    # Dynamic importance levels
    importance_levels: List[str] = [
        DefaultImportance.MAIN.value,
        DefaultImportance.SECONDARY.value,
        DefaultImportance.TERTIARY.value,
        DefaultImportance.EXTRA.value
    ]
    
    # Recommended attributes for entities in this canvas
    actor_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Personality"),
        AttributeTemplate(name="Likes"),
        AttributeTemplate(name="Dislikes"),
        AttributeTemplate(name="Secret"),
        AttributeTemplate(name="Weakness"),
    ]
    place_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Atmosphere"),
        AttributeTemplate(name="History"),
    ]
    item_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Condition"),
        AttributeTemplate(name="Value"),
    ]
    knowledge_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Source"),
        AttributeTemplate(name="Certainty"),
    ]

class Entity(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    attributes: Dict[str, str] = Field(default_factory=dict)
    x: float = 100.0
    y: float = 100.0

class Actor(Entity):
    importance: str = DefaultImportance.EXTRA.value

class Place(Entity):
    pass

class Item(Entity):
    pass

class Knowledge(Entity):
    pass

class RelationshipType(str, Enum):
    AGENCY = "agency"
    CAUSALITY = "causality"
    SENTIMENT = "sentiment"
    CHRONOTOPE = "chronotope"

class Relationship(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_uid: str
    target_uid: str
    rel_type: RelationshipType
    description: str
    attributes: Dict[str, str] = Field(default_factory=dict)

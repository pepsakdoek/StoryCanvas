from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

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
    importance_levels: List[str] = [
        DefaultImportance.MAIN.value,
        DefaultImportance.SECONDARY.value,
        DefaultImportance.TERTIARY.value,
        DefaultImportance.EXTRA.value
    ]
    actor_attributes: List[AttributeTemplate] = [
        AttributeTemplate(name="Personality"),
        AttributeTemplate(name="Likes"),
        AttributeTemplate(name="Dislikes"),
        AttributeTemplate(name="Secret"),
        AttributeTemplate(name="Weakness"),
    ]
    place_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Atmosphere")]
    item_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Condition")]
    knowledge_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Source")]
    snap_to_grid: bool = False
    grid_size: int = 20

# --- Global Identity ---
class EntityIdentity(BaseModel):
    uid: str
    name: str
    entity_type: str # "Actor", "Place", etc.
    importance: str = DefaultImportance.EXTRA.value

class GlobalRegistry(BaseModel):
    entities: Dict[str, EntityIdentity] = Field(default_factory=dict)

# --- Temporal State ---
class EntityState(BaseModel):
    uid: str
    x: float = 100.0
    y: float = 100.0
    attributes: Dict[str, str] = Field(default_factory=dict)

# --- Events ---
class Event(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: str = ""
    involved_uids: List[str] = Field(default_factory=list)
    location_uid: Optional[str] = None
    x: float = 500.0
    y: float = 500.0

class RelationshipType(str, Enum):
    AGENCY = "agency"
    CAUSALITY = "causality"
    SENTIMENT = "sentiment"
    CHRONOTOPE = "chronotope"
    POSSESSION = "possession" # For items held by actors
    LOCATION = "location"     # For entities located in places

class Relationship(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    source_uid: str
    target_uid: str
    rel_type: RelationshipType
    description: str
    attributes: Dict[str, str] = Field(default_factory=dict)

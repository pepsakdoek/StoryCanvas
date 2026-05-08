from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
import uuid

class DefaultImportance(str, Enum):
    MAIN = "main"
    SECONDARY = "secondary"
    TERTIARY = "tertiary"
    EXTRA = "extra"

class AttributeType(str, Enum):
    TEXT = "text"
    NUMBER = "number"
    SELECT = "select"

class AttributeTemplate(BaseModel):
    name: str
    description: str = ""
    attr_type: AttributeType = AttributeType.TEXT
    options: List[str] = Field(default_factory=list) # For SELECT type
    allow_custom: bool = False # Allow adding new options in GUI
    required: bool = False
    enabled: bool = True

class AppSettings(BaseModel):
    llm_endpoint: str = "http://localhost:11434/api/generate"
    llm_model: str = "phi:latest"
    snap_to_grid: bool = False
    grid_size: int = 20

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
    ]
    place_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Atmosphere")]
    item_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Condition")]
    knowledge_attributes: List[AttributeTemplate] = [AttributeTemplate(name="Source")]
    event_attributes: List[AttributeTemplate] = []

from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
import uuid

# ... (other models)

# --- Generator Response Models ---
class NameResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    names: List[str] = Field(default_factory=list)
    generation_source: str = "manual"

class TraitResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    traits: List[str] = Field(default_factory=list)
    generation_source: str = "manual"

class CharacterResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str = "Unknown"
    role: str = ""
    personality: str = ""
    traits: List[str] = Field(default_factory=list)
    generation_source: str = "manual"

class PlaceResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str = "Unknown"
    type: str = ""
    description: str = ""
    attributes: Dict[str, str] = Field(default_factory=dict)
    generation_source: str = "manual"

class ItemResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str = "Unknown"
    type: str = ""
    description: str = ""
    attributes: Dict[str, str] = Field(default_factory=dict)
    generation_source: str = "manual"

class KnowledgeResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str = "Unknown"
    type: str = ""
    description: str = ""
    attributes: Dict[str, str] = Field(default_factory=dict)
    generation_source: str = "manual"

class EventResponse(BaseModel):
    model_config = ConfigDict(extra='allow')
    name: str = "Unknown"
    description: str = ""
    involved_uids: List[str] = Field(default_factory=list)
    location_uid: str = ""
    x: int = 500
    y: int = 500
    generation_source: str = "manual"

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
    importance: str = DefaultImportance.EXTRA.value
    attributes: Dict[str, str] = Field(default_factory=dict)
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

# --- Prose ---
class Beat(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    text: str = ""

class Prose(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = ""
    beats: List[Beat] = Field(default_factory=list)
    content: Optional[str] = None # Legacy field for migration

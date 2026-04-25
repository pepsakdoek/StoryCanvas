from typing import Optional
from pydantic import BaseModel, Field
import uuid

class Actor(BaseModel):
    uid: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    description: Optional[str] = ""
    x: float = 100.0
    y: float = 100.0

import requests
import json
import random
from typing import List, Optional, Dict, Any
from .models import (
    NameResponse, TraitResponse, CharacterResponse, PlaceResponse, 
    ItemResponse, KnowledgeResponse, EventResponse
)
from pydantic import ValidationError

# Fallback procedural generators
VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

def generate_procedural_name(min_syllables=2, max_syllables=3) -> str:
    """Generate a random name using syllable concatenation."""
    length = random.randint(min_syllables, max_syllables)
    name = ""
    for _ in range(length):
        name += random.choice(CONSONANTS) + random.choice(VOWELS)
    return name.capitalize()

def generate_procedural_names(count: int) -> List[str]:
    """Generate multiple procedural names."""
    return [generate_procedural_name() for _ in range(count)]

def generate_procedural_traits(count: int = 3) -> List[str]:
    """Generate procedural personality traits."""
    traits = ["brave", "shy", "wise", "reckless", "kind", "cruel", "loyal", "deceitful", "curious", "apathetic"]
    return random.sample(traits, min(count, len(traits)))

def generate_procedural_place() -> Dict[str, Any]:
    """Generate a procedural place."""
    return {
        "name": generate_procedural_name(),
        "type": random.choice(["town", "forest", "castle", "cave", "ruin"]),
        "description": "A mysterious location waiting to be explored.",
        "attributes": {"size": random.choice(["small", "medium", "large"]), "danger": random.choice(["low", "medium", "high"])}
    }

def generate_procedural_item() -> Dict[str, Any]:
    """Generate a procedural item."""
    return {
        "name": generate_procedural_name(),
        "type": random.choice(["weapon", "tool", "artifact", "consumable"]),
        "description": "An object with unknown origins.",
        "attributes": {"rarity": random.choice(["common", "uncommon", "rare", "legendary"])}
    }

def generate_procedural_knowledge() -> Dict[str, Any]:
    """Generate a procedural knowledge entry."""
    return {
        "name": generate_procedural_name(),
        "type": random.choice(["secret", "lore", "map", "recipe"]),
        "description": "A fragment of forgotten wisdom.",
        "attributes": {"difficulty": random.choice(["easy", "medium", "hard"])}
    }

def generate_procedural_event() -> Dict[str, Any]:
    """Generate a procedural event."""
    return {
        "name": generate_procedural_name(),
        "description": "A significant occurrence in the story.",
        "involved_uids": [],
        "location_uid": "",
        "x": random.randint(0, 2000),
        "y": random.randint(0, 2000)
    }

def parse_llm_response(response_text: str, expected_model: type) -> Optional[Dict[str, Any]]:
    """Try to parse LLM response as JSON and validate with Pydantic."""
    try:
        # Try to extract JSON from response (in case of markdown or extra text)
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        else:
            json_str = response_text.strip()
        
        data = json.loads(json_str)
        return expected_model(**data).model_dump()
    except (json.JSONDecodeError, ValidationError, AttributeError):
        return None

def generate_with_llm(prompt: str, endpoint: str, model: str, expected_model: type) -> Optional[Dict[str, Any]]:
    """Send a prompt to a local Ollama-compatible LLM and return parsed JSON."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(endpoint, json=payload, timeout=15)
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "").strip()
        return parse_llm_response(response_text, expected_model)
    except Exception:
        # Silently fail, caller will handle fallback
        return None

def get_generator_prompt(gen_type: str, count: int = 1, custom_prompt: str = "") -> str:
    """Build prompt based on generator type."""
    if gen_type == "Names":
        return custom_prompt or (
            f"You are a creative name generator. "
            f"Return ONLY a JSON object with a 'names' array of {count} unique fantasy names. "
            f"Example: {{'names': ['Aelar', 'Kira', 'Thorne']}}"
        )
    elif gen_type == "Traits":
        return custom_prompt or (
            f"You are a trait randomizer. "
            f"Return ONLY a JSON object with a 'traits' array of {count} personality traits. "
            f"Example: {{'traits': ['brave', 'wise', 'loyal']}}"
        )
    elif gen_type == "Character":
        return custom_prompt or (
            "You are a character generator. "
            "Return ONLY a JSON object with keys: name, role, personality, and traits (array of 2-4 traits). "
            "Example: {'name': 'Kira', 'role': 'warrior', 'personality': 'brave', 'traits': ['loyal', 'fierce', 'honest']}"
        )
    elif gen_type == "Place":
        return custom_prompt or (
            "You are a place generator. "
            "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
            "Example: {'name': 'Eldoria', 'type': 'forest', 'description': 'A mystical woodland', 'attributes': {'danger': 'low', 'size': 'large'}}"
        )
    elif gen_type == "Item":
        return custom_prompt or (
            "You are an item generator. "
            "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
            "Example: {'name': 'Shadowblade', 'type': 'weapon', 'description': 'A blade that drinks light', 'attributes': {'rarity': 'rare', 'damage': 'high'}}"
        )
    elif gen_type == "Knowledge":
        return custom_prompt or (
            "You are a knowledge generator. "
            "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
            "Example: {'name': 'The Lost Ritual', 'type': 'secret', 'description': 'A forgotten ceremony', 'attributes': {'difficulty': 'hard'}}"
        )
    elif gen_type == "Event":
        return custom_prompt or (
            "You are an event generator. "
            "Return ONLY a JSON object with keys: name, description, involved_uids (array of strings), location_uid (string), x (int), y (int). "
            "Note: `involved_uids` and `location_uid` are placeholders for linking to existing entities. "
            "Example: {'name': 'The Battle', 'description': 'A clash between two factions', 'involved_uids': ['UID1', 'UID2'], 'location_uid': 'PLACE1', 'x': 500, 'y': 600}"
        )
    return custom_prompt or "Generate something creative."

def get_expected_model(gen_type: str) -> type:
    """Return the expected Pydantic model for a generator type."""
    mapping = {
        "Names": NameResponse,
        "Traits": TraitResponse,
        "Character": CharacterResponse,
        "Place": PlaceResponse,
        "Item": ItemResponse,
        "Knowledge": KnowledgeResponse,
        "Event": EventResponse
    }
    return mapping.get(gen_type, NameResponse)

def analyze_prose(text: str, endpoint: str, model: str) -> Optional[str]:
    """Send prose to LLM for analysis/entity extraction."""
    prompt = (
        f"Analyze the following story text and identify potential Actors, Places, Items, Knowledge, and Events. "
        f"Return a summary of what you found.\n\nText: {text}"
    )
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception:
        return None

def generate_any(gen_type: str, endpoint: str, model: str, count: int = 1, custom_prompt: str = "", force_procedural: bool = False) -> Dict[str, Any]:
    """Unified generator function with LLM and procedural fallback."""
    if not force_procedural:
        prompt = get_generator_prompt(gen_type, count, custom_prompt)
        expected_model = get_expected_model(gen_type)
        result = generate_with_llm(prompt, endpoint, model, expected_model)
        if result:
            return result
    
    # Fallback
    if gen_type == "Names":
        return {"names": generate_procedural_names(count)}
    elif gen_type == "Traits":
        return {"traits": generate_procedural_traits(count)}
    elif gen_type == "Character":
        return {
            "name": generate_procedural_name(),
            "role": "adventurer",
            "personality": "curious",
            "traits": generate_procedural_traits(3)
        }
    elif gen_type == "Place":
        return generate_procedural_place()
    elif gen_type == "Item":
        return generate_procedural_item()
    elif gen_type == "Knowledge":
        return generate_procedural_knowledge()
    elif gen_type == "Event":
        return generate_procedural_event()
    
    return {"names": [generate_procedural_name()]}

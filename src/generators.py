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
    import logging
    try:
        # 1. Try to extract from <JSON> tags (new preferred method)
        if "<JSON>" in response_text and "</JSON>" in response_text:
            start = response_text.find("<JSON>") + 6
            end = response_text.find("</JSON>", start)
            json_str = response_text[start:end].strip()
        # 2. Try markdown backticks
        elif "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            json_str = response_text[start:end].strip()
        # 3. Fallback to raw braces
        else:
            start = response_text.find("{")
            end = response_text.rfind("}")
            if start != -1 and end != -1:
                json_str = response_text[start:end+1].strip()
            else:
                json_str = response_text.strip()
        
        data = json.loads(json_str)
        
        # Smart Handling: If we wanted names (list) but got a single entity (dict with 'name')
        if expected_model == NameResponse and "names" not in data and "name" in data:
            data = {"names": [data["name"]]}
            
        # Validate and return everything (extra='allow' ensures non-schema fields are kept)
        return expected_model(**data).model_dump()
    except json.JSONDecodeError as e:
        logging.error(f"LLM JSON Decode Error: {e}. Raw text: {response_text[:500]}...")
        return None
    except ValidationError as e:
        logging.error(f"LLM Validation Error: {e}. Data: {json_str[:500]}...")
        return None
    except Exception as e:
        logging.error(f"LLM Parse Error: {e}")
        return None

def generate_with_llm(prompt: str, endpoint: str, model: str, expected_model: type) -> Optional[Dict[str, Any]]:
    """Send a prompt to a local Ollama-compatible LLM and return parsed JSON."""
    import logging
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
            # Removed "format": "json" to allow vocal models to provide context around tags
        }
        logging.info(f"Sending LLM request to {endpoint} (Model: {model})")
        response = requests.post(endpoint, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        response_text = data.get("response", "").strip()
        if not response_text:
            logging.warning("LLM returned empty response")
            return None
        return parse_llm_response(response_text, expected_model)
    except requests.exceptions.RequestException as e:
        logging.error(f"LLM Request Failed: {e}")
        return None
    except Exception as e:
        logging.error(f"LLM Unexpected Error: {e}")
        return None

def get_generator_prompt(gen_type: str, count: int = 1, custom_prompt: str = "") -> str:
    """Build prompt based on generator type."""
    tag_instruction = "IMPORTANT: You MUST wrap your final JSON object in <JSON> and </JSON> tags. You may provide conversational context outside of these tags."
    
    if gen_type == "Names":
        return (custom_prompt or f"Generate {count} unique fantasy names.") + f"\n{tag_instruction}\nExample: <JSON>{{\"names\": [\"Aelar\", \"Kira\"]}}</JSON>"
    
    elif gen_type == "Traits":
        return (custom_prompt or f"Generate {count} personality traits.") + f"\n{tag_instruction}\nExample: <JSON>{{\"traits\": [\"brave\", \"loyal\"]}}</JSON>"
    
    elif gen_type == "Character":
        return (custom_prompt or "Generate a detailed character.") + f"\n{tag_instruction}\nExample: <JSON>{{\"name\": \"Kira\", \"role\": \"warrior\", \"personality\": \"brave\", \"traits\": [\"loyal\", \"fierce\"]}}</JSON>"
    
    elif gen_type == "Place":
        return (custom_prompt or "Generate a mystical location.") + f"\n{tag_instruction}\nExample: <JSON>{{\"name\": \"Eldoria\", \"type\": \"forest\", \"description\": \"A mystical woodland\", \"attributes\": {{\"danger\": \"low\"}}}}</JSON>"
    
    elif gen_type == "Item":
        return (custom_prompt or "Generate a storied item.") + f"\n{tag_instruction}\nExample: <JSON>{{\"name\": \"Shadowblade\", \"type\": \"weapon\", \"description\": \"A dark blade\", \"attributes\": {{\"rarity\": \"rare\"}}}}</JSON>"
    
    elif gen_type == "Knowledge":
        return (custom_prompt or "Generate a fragment of lore or a secret.") + f"\n{tag_instruction}\nExample: <JSON>{{\"name\": \"The Ritual\", \"type\": \"secret\", \"description\": \"A lost ceremony\", \"attributes\": {{\"difficulty\": \"hard\"}}}}</JSON>"
    
    elif gen_type == "Event":
        return (custom_prompt or "Generate a narrative event.") + f"\n{tag_instruction}\nExample: <JSON>{{\"name\": \"The Clash\", \"description\": \"A battle\", \"involved_uids\": [], \"location_uid\": \"\", \"x\": 500, \"y\": 600}}</JSON>"
    
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
            result['generation_source'] = 'llm'
            return result
    
    # Fallback
    res = {}
    if gen_type == "Names":
        res = {"names": generate_procedural_names(count)}
    elif gen_type == "Traits":
        res = {"traits": generate_procedural_traits(count)}
    elif gen_type == "Character":
        res = {
            "name": generate_procedural_name(),
            "role": "adventurer",
            "personality": "curious",
            "traits": generate_procedural_traits(3)
        }
    elif gen_type == "Place":
        res = generate_procedural_place()
    elif gen_type == "Item":
        res = generate_procedural_item()
    elif gen_type == "Knowledge":
        res = generate_procedural_knowledge()
    elif gen_type == "Event":
        res = generate_procedural_event()
    else:
        res = {"names": [generate_procedural_name()]}
    
    res['generation_source'] = 'procedural'
    return res

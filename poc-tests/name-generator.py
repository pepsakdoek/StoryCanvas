import requests
import json
import random
from nicegui import ui
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any

# Default local LLM endpoint
LLM_ENDPOINT = "http://localhost:11434/api/generate"
LLM_MODEL = "phi:latest"

# Fallback procedural generators
VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

def generate_procedural_name(min_syllables=2, max_syllables=3) -> str:
    """Generate a random name using syllable拼接."""
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
        "involved_uids": [],  # TODO: link to existing entities
        "location_uid": "",   # TODO: link to existing place
        "x": random.randint(0, 2000),
        "y": random.randint(0, 2000)
    }

# Pydantic models for validation
class NameResponse(BaseModel):
    names: List[str]

class TraitResponse(BaseModel):
    traits: List[str]

class CharacterResponse(BaseModel):
    name: str
    role: str
    personality: str
    traits: List[str]

class PlaceResponse(BaseModel):
    name: str
    type: str
    description: str
    attributes: Dict[str, str]

class ItemResponse(BaseModel):
    name: str
    type: str
    description: str
    attributes: Dict[str, str]

class KnowledgeResponse(BaseModel):
    name: str
    type: str
    description: str
    attributes: Dict[str, str]

class EventResponse(BaseModel):
    name: str
    description: str
    # TODO: `involved_uids` and `location_uid` will be linked to existing entities
    involved_uids: List[str]  # placeholder: will be populated via UI selection
    location_uid: str        # placeholder: will be populated via UI selection
    x: int
    y: int

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
    except Exception as e:
        ui.notify(f"LLM error: {str(e)}", type="negative")
        return None

# UI
ui.page_title("LLM Generator")

with ui.column().classes("w-full max-w-2xl mx-auto p-4 gap-4"):
    ui.label("LLM Generator").classes("text-2xl font-bold text-slate-800")
    
    # Endpoint configuration
    with ui.row().classes("w-full items-center gap-2"):
        ui.label("Endpoint:").classes("text-sm font-medium text-slate-600")
        endpoint_input = ui.input(
            value=LLM_ENDPOINT, 
            placeholder="http://localhost:11434/api/generate"
        ).classes("flex-grow")
        model_input = ui.input(
            value=LLM_MODEL, 
            placeholder="phi:latest"
        ).classes("w-32")
    
    # Generator type selector
    generator_type = ui.select(
        ["Names", "Traits", "Character", "Place", "Item", "Knowledge", "Event"],
        value="Names"
    ).classes("w-32")
    
    # Count input (only for Names/Traits)
    count_input = ui.number(
        label="Count", 
        value=1, 
        min=1, 
        max=10, 
        step=1
    ).classes("w-24")
    
    # Custom prompt input (optional override)
    custom_prompt_input = ui.input(
        placeholder="Custom prompt (optional)",
        value=""
    ).classes("w-full")
    
    # Output area
    output_label = ui.label("Generated output will appear here").classes(
        "p-4 bg-slate-50 border border-slate-200 rounded-lg text-sm font-mono text-slate-700 whitespace-pre-wrap"
    )
    
    def generate():
        gen_type = generator_type.value
        count = int(count_input.value)
        endpoint = endpoint_input.value.strip()
        model = model_input.value.strip()
        custom_prompt = custom_prompt_input.value.strip()
        
        # Build prompt and expected model based on type
        if gen_type == "Names":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    f"You are a creative name generator. "
                    f"Return ONLY a JSON object with a 'names' array of {count} unique fantasy names. "
                    f"Example: {{'names': ['Aelar', 'Kira', 'Thorne']}}"
                )
            expected_model = NameResponse
        elif gen_type == "Traits":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    f"You are a trait randomizer. "
                    f"Return ONLY a JSON object with a 'traits' array of {count} personality traits. "
                    f"Example: {{'traits': ['brave', 'wise', 'loyal']}}"
                )
            expected_model = TraitResponse
        elif gen_type == "Character":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    "You are a character generator. "
                    "Return ONLY a JSON object with keys: name, role, personality, and traits (array of 2-4 traits). "
                    "Example: {'name': 'Kira', 'role': 'warrior', 'personality': 'brave', 'traits': ['loyal', 'fierce', 'honest']}"
                )
            expected_model = CharacterResponse
        elif gen_type == "Place":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    "You are a place generator. "
                    "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
                    "Example: {'name': 'Eldoria', 'type': 'forest', 'description': 'A mystical woodland', 'attributes': {'danger': 'low', 'size': 'large'}}"
                )
            expected_model = PlaceResponse
        elif gen_type == "Item":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    "You are an item generator. "
                    "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
                    "Example: {'name': 'Shadowblade', 'type': 'weapon', 'description': 'A blade that drinks light', 'attributes': {'rarity': 'rare', 'damage': 'high'}}"
                )
            expected_model = ItemResponse
        elif gen_type == "Knowledge":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    "You are a knowledge generator. "
                    "Return ONLY a JSON object with keys: name, type, description, and attributes (key-value strings). "
                    "Example: {'name': 'The Lost Ritual', 'type': 'secret', 'description': 'A forgotten ceremony', 'attributes': {'difficulty': 'hard'}}"
                )
            expected_model = KnowledgeResponse
        elif gen_type == "Event":
            if custom_prompt:
                system_prompt = custom_prompt
            else:
                system_prompt = (
                    "You are an event generator. "
                    "Return ONLY a JSON object with keys: name, description, involved_uids (array of strings), location_uid (string), x (int), y (int). "
                    "Note: `involved_uids` and `location_uid` are placeholders for linking to existing entities. "
                    "Example: {'name': 'The Battle', 'description': 'A clash between two factions', 'involved_uids': ['UID1', 'UID2'], 'location_uid': 'PLACE1', 'x': 500, 'y': 600}"
                )
            expected_model = EventResponse
        else:
            system_prompt = custom_prompt or "Generate something creative."
            expected_model = NameResponse
        
        # Try LLM first
        result = generate_with_llm(system_prompt, endpoint, model, expected_model)
        
        if result:
            output_label.set_text(json.dumps(result, indent=2))
        else:
            # Fallback procedural generation
            if gen_type == "Names":
                fallback = {"names": generate_procedural_names(count)}
            elif gen_type == "Traits":
                fallback = {"traits": generate_procedural_traits(count)}
            elif gen_type == "Character":
                fallback = {
                    "name": generate_procedural_name(),
                    "role": "adventurer",
                    "personality": "curious",
                    "traits": generate_procedural_traits(3)
                }
            elif gen_type == "Place":
                fallback = generate_procedural_place()
            elif gen_type == "Item":
                fallback = generate_procedural_item()
            elif gen_type == "Knowledge":
                fallback = generate_procedural_knowledge()
            elif gen_type == "Event":
                fallback = generate_procedural_event()
            else:
                fallback = {"names": [generate_procedural_name()]}
            
            output_label.set_text(json.dumps(fallback, indent=2))
            ui.notify("LLM failed; used procedural fallback", type="warning")
    
    # Generate button
    ui.button("Generate", on_click=generate).classes(
        "w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-lg"
    )
    
    # Procedural-only fallback button
    def generate_procedural_only():
        gen_type = generator_type.value
        count = int(count_input.value)
        
        if gen_type == "Names":
            result = {"names": generate_procedural_names(count)}
        elif gen_type == "Traits":
            result = {"traits": generate_procedural_traits(count)}
        elif gen_type == "Character":
            result = {
                "name": generate_procedural_name(),
                "role": "adventurer",
                "personality": "curious",
                "traits": generate_procedural_traits(3)
            }
        elif gen_type == "Place":
            result = generate_procedural_place()
        elif gen_type == "Item":
            result = generate_procedural_item()
        elif gen_type == "Knowledge":
            result = generate_procedural_knowledge()
        elif gen_type == "Event":
            result = generate_procedural_event()
        else:
            result = {"names": [generate_procedural_name()]}
        
        output_label.set_text(json.dumps(result, indent=2))
    
    ui.button("Fallback: Procedural Only", on_click=generate_procedural_only).classes(
        "w-full bg-slate-600 hover:bg-slate-700 text-white font-semibold py-2 rounded-lg"
    )

ui.run(title="LLM Generator")

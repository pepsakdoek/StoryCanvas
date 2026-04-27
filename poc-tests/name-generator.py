import requests
import json
import random
from nicegui import ui
from pydantic import BaseModel, ValidationError
from typing import List, Optional, Dict, Any

# Default local LLM endpoint
LLM_ENDPOINT = "http://localhost:11434/api/generate"
LLM_MODEL = "phi:latest"

# Fallback procedural name generators
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
ui.page_title("LLM Name & Trait Generator")

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
        ["Names", "Traits", "Character"],
        value="Names"
    ).classes("w-32")
    
    # Count input (only for Names/Traits)
    count_input = ui.number(
        label="Count", 
        value=3, 
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
        
        # Build prompt based on type
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
        else:
            result = {"names": [generate_procedural_name()]}
        
        output_label.set_text(json.dumps(result, indent=2))
    
    ui.button("Fallback: Procedural Only", on_click=generate_procedural_only).classes(
        "w-full bg-slate-600 hover:bg-slate-700 text-white font-semibold py-2 rounded-lg"
    )

ui.run(title="LLM Generator")

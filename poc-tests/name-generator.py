import requests
import json
import random
from nicegui import ui, app
from starlette.responses import PlainTextResponse

# Default local LLM endpoint
LLM_ENDPOINT = "http://localhost:11434/api/generate"
LLM_MODEL = "phi:latest"

# Fallback procedural name generators
SYLLABLES = ["ar", "el", "in", "or", "un", "ka", "mi", "to", "na", "ri", "ve", "la", "si", "do", "cu"]
VOWELS = "aeiou"
CONSONANTS = "bcdfghjklmnpqrstvwxyz"

def generate_procedural_name(min_syllables=2, max_syllables=3):
    """Generate a random name using syllable拼接."""
    length = random.randint(min_syllables, max_syllables)
    name = ""
    for _ in range(length):
        name += random.choice(CONSONANTS) + random.choice(VOWELS)
    return name.capitalize()

def generate_name_with_llm(prompt: str, endpoint: str, model: str) -> str:
    """Send a prompt to a local Ollama-compatible LLM and return the generated name."""
    try:
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False
        }
        response = requests.post(endpoint, json=payload, timeout=10)
        response.raise_for_status()
        data = response.json()
        return data.get("response", "").strip()
    except Exception as e:
        return f"[LLM error: {str(e)}]"

# UI
ui.page_title("Name Generator")

with ui.column().classes("w-full max-w-2xl mx-auto p-4 gap-4"):
    ui.label("Local LLM Name Generator").classes("text-2xl font-bold text-slate-800")
    
    # Endpoint configuration
    with ui.row().classes("w-full items-center gap-2"):
        ui.label("LLM Endpoint:").classes("text-sm font-medium text-slate-600")
        endpoint_input = ui.input(
            value=LLM_ENDPOINT, 
            placeholder="http://localhost:11434/api/generate"
        ).classes("flex-grow")
        model_input = ui.input(
            value=LLM_MODEL, 
            placeholder="phi:latest"
        ).classes("w-32")
    
    # Prompt configuration
    with ui.row().classes("w-full items-center gap-2"):
        ui.label("Name Type:").classes("text-sm font-medium text-slate-600")
        name_type = ui.select(
            ["Fantasy", "Sci-Fi", "Modern", "Mythological", "Custom"],
            value="Fantasy"
        ).classes("w-40")
    
    # Input area
    prompt_input = ui.input(
        placeholder="Describe the name you want (e.g., 'a strong female elven name')",
        value="Generate one fantasy name for a brave warrior."
    ).classes("w-full")
    
    # Output area
    output_label = ui.label("Generated name will appear here").classes(
        "p-4 bg-slate-50 border border-slate-200 rounded-lg text-lg font-medium text-slate-700"
    )
    
    def generate():
        name_type_val = name_type.value
        prompt_text = prompt_input.value.strip()
        endpoint = endpoint_input.value.strip()
        model = model_input.value.strip()
        
        # Build system prompt
        system_prompt = (
            f"You are a creative name generator. "
            f"Return ONLY the name(s), no explanation. "
            f"Generate {name_type_val.lower()} name(s). "
            f"User request: '{prompt_text}'. "
            f"Return 1-3 comma-separated names."
        )
        
        # Try LLM first
        result = generate_name_with_llm(system_prompt, endpoint, model)
        
        # Fallback if LLM fails or returns error text
        if "error" in result.lower() or len(result) < 2:
            result = generate_procedural_name()
        
        output_label.set_text(result)
    
    # Generate button
    ui.button("Generate Name", on_click=generate).classes("w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 rounded-lg")
    
    # Procedural fallback button
    def generate_procedural():
        output_label.set_text(generate_procedural_name())
    
    ui.button("Fallback: Procedural Name", on_click=generate_procedural).classes(
        "w-full bg-slate-600 hover:bg-slate-700 text-white font-semibold py-2 rounded-lg"
    )

ui.run(title="Name Generator")

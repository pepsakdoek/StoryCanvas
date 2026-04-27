# Project: Story creation and narrative visualisation assistance (Story CANVAs)

## Overview
A data-driven, emergent narrative game. The goal is to provide a "blank canvas" where users (or AI agents) can procedurally generate or manually define the building blocks of a story.

## Core Components (The Data Structure)
- **Entities (Nouns):** Actors, Places, Items, Knowledge, Events and Relationships.
    - **Modular Attributes:** Entities have a flexible attribute system. Only `importance` is mandatory for Actors. All other traits (personality, secrets, etc.) are dynamic key-value pairs.
    - **Attribute Schema:** Each canvas can define a list of "recommended" or "required" attribute templates to guide the user.
- **Relationships (Verbs):** Agency, Causality, Sentiment, and Chronotopes.
- **Hierarchy:** Fractal scaling for locations (Room > Building > Town > World).
- **The Registry:** A centralized UID-based system to track all world states.

## Technical Stack
- **Language:** Python 3.12+ (managed via `uv`).
    - Use `uv run python StoryCanvas.py` to start the application.
    - Use `uv run python StoryCanvas.py --cli` for CLI mode.
- **UI:** NiceGUI (for a reactive, web-based dashboard).
- **Data Structures:** json files so that they are vaguely human readable and quickly parsable by cli and a programming language.
- **Data Validation:** pydantic will make sure the json created by llms or other code is valid and can be inserted into the files.
- **Intelligence:** Gemini API (cloud) and Ollama (local) for narrative generation and "Lucky" button flavors.
    - **LLM Settings:** Managed via global `AppSettings` (`llm_endpoint`, `llm_model`). Defaults to local Ollama (`http://localhost:11434/api/generate`).
    - **Generator:** Integrated `src/generators.py` provides both LLM-powered and procedural fallback generation for Names, Traits, Characters, Places, Items, Knowledge, and Events.
- **Interface:** Dual-mode (Web UI + CLI for agent-based testing).

## Development Notes
- **Execution:** Always prefer `uv run` to ensure dependencies like `nicegui` and `pydantic` are correctly resolved from the virtual environment.
- **Main Menu:** Includes 'Create', 'Load', 'Help' (opens `documentation/usage.md`), and 'Exit' (shuts down the server).
- **Documentation:** `documentation/usage.md` contains the primary end-user guide.
- **Logs:** Application logs are automatically generated in the `/logs` directory with timestamps.

## Folder Architecture
The "Canvas" uses a hierarchical directory structure. This allows for persistent "World" data while keeping individual "Stories" modular via temporal "Slots" (Chapters).

```text
/save
    /app_settings.json       <-- Global Application settings (LLM, Grid)
    /{Canvas_name}
        /registry.json       <-- The 'Global Registry' (UIDs mapped to Names & Types)
        /settings.json       <-- Story-level schema (Attributes, Importance levels)
        /slots/              <-- Temporal snapshots (e.g., Chapters)
            /{Slot_Name}/
                /States.json         <-- Position and attribute values for entities
                /Events.json         <-- Narrative events occurring in this slot
                /Relationships.json  <-- Links and memories active in this slot
                /Prose.json          <-- Markdown narrative text for this slot
```

## Narrative Logic
The engine focuses on **Causality** over **Chronology**. Events are data packets that modify the state of the world, creating a "History Log" that turns random objects into storied artifacts.
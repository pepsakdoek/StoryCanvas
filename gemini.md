# Project: Story creation and narrative visualisation assistance (Story CANVAs)

## Overview
A data-driven, emergent narrative game. The goal is to provide a "blank canvas" where users (or AI agents) can procedurally generate or manually define the building blocks of a story.

## Core Components (The Data Structure)
- **Entities (Nouns):** Actors, Places, Items, and Knowledge.
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
    - **LLM Settings:** Managed via `CanvasSettings` (`llm_endpoint`, `llm_model`). Defaults to local Ollama (`http://localhost:11434/api/generate`).
    - **Generator:** Integrated `src/generators.py` provides both LLM-powered and procedural fallback generation for Names, Traits, Characters, Places, Items, Knowledge, and Events.
- **Interface:** Dual-mode (Web UI + CLI for agent-based testing).

## Development Notes
- **Execution:** Always prefer `uv run` to ensure dependencies like `nicegui` and `pydantic` are correctly resolved from the virtual environment.
- **Main Menu:** Includes 'Create', 'Load', 'Help' (opens `documentation/usage.md`), and 'Exit' (shuts down the server).
- **Documentation:** `documentation/usage.md` contains the primary end-user guide.
- **Logs:** Application logs are automatically generated in the `/logs` directory with timestamps.

## Folder Architecture
The "Canvas" uses a hierarchical directory structure. This allows for persistent "World" data while keeping individual "Stories" modular.

```text
/Canvas_name
    /Actors.json         <-- The 'Cast' of characters
    /Places.json         <-- The 'Map' of locations
    /Knowledge.json      <-- The 'Library' of secrets/facts
    /Items.json          <-- The 'Vault' of physical objects
    /Relationships.json  <-- The 'Web' of links and memories
    /Time.json           <-- Most canvasses will just have 'normal' Gregorian time, but each 'world' in a system might have a different time system
```

## Narrative Logic
The engine focuses on **Causality** over **Chronology**. Events are data packets that modify the state of the world, creating a "History Log" that turns random objects into storied artifacts.
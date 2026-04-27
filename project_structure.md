# Project Structure Summary 

## Core Application Files 

`StoryCanvas.py`    Main entry point for the CLI application; sets up logging and runs the main application loop. 

`src/__init__.py`   Package initializer for the `src` module. 
`src/cli.py`        Command-line interface logic, including entity listing, attribute input, and generator/editing subcommands. 
`src/generators.py` Procedural generation and LLM integration for names, traits, places, items, knowledge, and events.
`src/models.py`     Pydantic models defining data structures for entities, events, relationships, prose, settings, and LLM responses.
`src/storage.py`    State management and persistence logic for canvases, slots, entities, events, relationships, and settings.

## GUI Components (`src/gui/`) 

`src/gui/__init__.py`           Package initializer for the GUI module. 
`src/gui/app.py`                Main GUI class (`StoryCanvasGUI`) managing UI state, canvas rendering, drag-and-drop, and event handling.
`src/gui/canvas_manager.py`     Handles UI rendering of the canvas, including entity/event cards and relationship lines. 
`src/gui/dialog_manager.py`     Central manager for opening and coordinating all modal dialogs (add/edit entity/event/relationship/slot/settings/generator).
`src/gui/dialog_utils.py`       Utility functions for building forms and populating attribute containers in dialogs.
`src/gui/entity_dialog.py`      Dialog logic for adding and editing entity cards (characters, places, items, etc.). 
`src/gui/event_dialog.py`       Dialog logic for adding and editing events (plot points, scenes). 
`src/gui/relationship_dialog.py`    Dialog logic for adding and editing relationships between entities. 
`src/gui/slot_dialog.py`        Dialog logic for creating and editing story slots (e.g., chapters or time periods). 
`src/gui/settings_dialog.py`    Dialog for managing global and canvas-specific settings, including attribute templates and importance levels. 
`src/gui/generator_dialog.py`   Dialog for triggering procedural or LLM-based generation and saving results to the canvas. 
`src/gui/styles.py`             CSS styling setup for the GUI using Quasar/Tailwind-like classes. 


## Tests & Proofs of Concept (`poc-tests/`)

`poc-tests/drag-drop-test.py`   Standalone test demonstrating drag-and-drop functionality for canvas objects.
`poc-tests/name-generator.py`   Standalone procedural name and trait generator (likely duplicated from `src/generators.py`).

## Configuration & Documentation 

`.gitignore`        Git ignore rules.
`.python-version`   Python version specification (e.g., for `pyenv`).
`LLM_GUIDE.md`      Documentation for LLM integration usage and configuration. 
`LLMfiles`          A folder where AIs should put their plan.md and other files they might usually not share
`README.md`         Project overview and usage instructions.
`pyproject.toml`    Project metadata, dependencies, and build configuration.
`todo.md`           Project TODO list. 
`documentation/usage.md`    Detailed usage documentation.
`gemini.md`         Gemini-specific notes or prompts (likely for AI-assisted development).
`cli-test.md`       Test cases or examples for CLI functionality.
# Source Code Index

This index provides a brief overview of all active source files in the StoryCanvas project.

## Root Entry Point
*   `StoryCanvas.py`: Main entry point that initializes logging and launches either the GUI or CLI mode.

## Core Logic (`src/`)
*   `src/cli.py`: Implements the command-line interface and terminal-based user workflow.
*   `src/generators.py`: Handles procedural and LLM-powered generation of names, entities, and events.
*   `src/models.py`: Defines the Pydantic data models for entities, relationships, events, and settings.
*   `src/storage.py`: Manages file system persistence, directory structures, and canvas state transitions.

## GUI Layer (`src/gui/`)
*   `src/gui/app.py`: Orchestrates the main NiceGUI layout, header bar, and prose panel.
*   `src/gui/canvas_manager.py`: Manages the interactive visual canvas, including rendering and positioning of entities.
*   `src/gui/dialog_manager.py`: Central controller for opening and managing the state of various UI dialogs.
*   `src/gui/dialog_utils.py`: Provides reusable UI components for dialogs, such as dynamic attribute field builders.
*   `src/gui/entity_dialog.py`: Handles the user interface for creating and editing Actors, Places, Items, and Knowledge.
*   `src/gui/event_dialog.py`: Manages the user interface for creating and editing narrative events.
*   `src/gui/generator_dialog.py`: Provides the interface for random content generation and saving results to the canvas.
*   `src/gui/relationship_dialog.py`: Handles the user interface for creating and editing links between entities and events.
*   `src/gui/settings_dialog.py`: Manages the configuration of global application settings and canvas-specific schemas.
*   `src/gui/slot_dialog.py`: Provides the interface for creating, switching, and managing chapters (slots).
*   `src/gui/styles.py`: Defines the CSS styles and visual themes used throughout the NiceGUI application.

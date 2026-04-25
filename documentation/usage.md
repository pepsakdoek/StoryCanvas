# Usage Guide

This document explains how to use the Bard Blank Canvas Narrative Engine interfaces.

## Interfaces

Bard provides two ways to interact with the engine: a Graphical User Interface (GUI) and a Command Line Interface (CLI).

### Graphical User Interface (GUI)

The GUI is the default mode when running the application. It provides a blank canvas for story building.

**How to run:**
```bash
uv run bard.py
```

**Features:**
- **Canvas:** A white background with a faint 100x100 pixel grid (0.1 opacity).
- **Context Menu:** Right-click anywhere on the canvas to bring up the context menu.
    - **Add:** Opens a dialog to create a new Actor.
    - **Exit:** Closes the application.
- **Add Actor Dialog:** Enter the name and description for the new actor. Once saved, the data is persisted to `Actors.json`.

### Command Line Interface (CLI)

The CLI is useful for quick data entry or automated testing.

**How to run:**
```bash
uv run bard.py --cli
```

**Features:**
- **Interactive Prompts:** The CLI will prompt you for the actor's name and description.
- **Validation:** Ensures that a name is provided before saving.
- **Persistence:** Data is saved to `Actors.json` in the same format as the GUI.

## Data Storage

All actors are stored in `Actors.json` in the project root. Each actor has:
- `uid`: A unique identifier (UUID v4).
- `name`: The display name of the actor.
- `description`: A brief description or bio.

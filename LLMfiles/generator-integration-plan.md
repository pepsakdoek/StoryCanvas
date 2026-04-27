# Generator Integration Plan

## Goal
Integrate the random generator logic from `poc-tests/name-generator.py` into the main `StoryCanvas` codebase.

## Proposed Changes

### 1. Data Models (`src/models.py`)
- Update `CanvasSettings` to include:
    - `llm_endpoint`: str (default: "http://localhost:11434/api/generate")
    - `llm_model`: str (default: "phi:latest")
- Add Pydantic models for LLM responses (imported/adapted from `poc-tests/name-generator.py`):
    - `NameResponse`, `TraitResponse`, `CharacterResponse`, `PlaceResponse`, `ItemResponse`, `KnowledgeResponse`, `EventResponse`.

### 2. Generator Logic (`src/generators.py`)
- Create this new module to house:
    - Procedural generation functions (`generate_procedural_name`, etc.).
    - LLM generation functions (`generate_with_llm`, `parse_llm_response`).
    - A unified `Generator` class or set of functions that handle both LLM and fallback.

### 3. Storage Layer (`src/storage.py`)
- (No changes needed if `CanvasSettings` is used, as it's already handled).

### 4. GUI Integration (`src/gui/app.py` & `src/gui/dialogs.py`)
- **Settings:** Add fields to edit `llm_endpoint` and `llm_model` in the UI (maybe a "Settings" tab or dialog).
- **Generator UI:**
    - Option A: A new "Generator" tab.
    - Option B: A floating dialog accessible from the canvas.
    - Given the user wants to "Save to Canvas", a dialog or a side-panel might be best.
    - Let's go with a new "Generator" tab for now to match the "Prose" tab pattern, or a dialog if it feels more like a utility.
    - Actually, a dialog triggered by a "Lucky" button or a "Generate" button in the header might be nice.

### 5. CLI Integration (`src/cli.py`)
- Add an option to the main menu for "Random Generator".
- Allow generating and optionally saving to the current canvas.

## Tasks
1. [ ] Update `src/models.py` with LLM settings and response models.
2. [ ] Create `src/generators.py` with logic from POC.
3. [ ] Update `src/gui/app.py` to include LLM settings in the UI.
4. [ ] Implement Generator UI (Tab or Dialog) in `src/gui/`.
5. [ ] Add "Save to Canvas" functionality to the Generator.
6. [ ] Update `src/cli.py` with Generator options.
7. [ ] Update `gemini.md` with notes.

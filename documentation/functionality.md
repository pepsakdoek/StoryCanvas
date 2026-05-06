# StoryCanvas GUI Functionality List

This document lists all functionalities available in the StoryCanvas GUI that involve data modification or persistence. This serves as a checklist to ensure that all core features can eventually be performed via the CLI as well.

(Status: ✅ = Available, ❌ = Not Available. Format: [GUI][CLI])

## 1. Canvas Management
*   ✅✅ **List Canvases:** View all available story canvases.
*   ✅✅ **Create Canvas:** Initialize a new canvas directory with default settings.
*   ✅✅ **Load Canvas:** Open an existing canvas and load its registry and settings.

## 2. Chapter (Slot) Management
*   ✅✅ **List Chapters:** View all temporal slots (chapters) within the current canvas.
*   ✅✅ **Create Chapter:** Create a new slot.
    *   *Option:* Clone state from the currently active chapter.
*   ✅✅ **Switch Chapter:** Load the state, events, relationships, and prose of a specific chapter.
*   ❌✅ **Delete Chapter:** Remove a chapter and all its associated data from the canvas.

## 3. Entity Management (Actors, Places, Items, Knowledge)
*   ✅✅ **Add Entity:** Create a new entity of a specific type.
*   ✅❌ **Edit Entity:**
    *   Modify Global Name (Identity).
    *   Modify Importance level.
    *   Modify Position (X, Y coordinates).
    *   Modify Attributes (based on schema).
*   ✅✅ **Delete Entity:** Remove an entity's state from the current chapter and clear its relationships.
*   ✅❌ **Auto-Arrange:** Deterministically reposition all entities on the canvas based on type and importance.
*   ✅❌ **Toggle Visibility:** Filter entities on the canvas by type.
*   ✅❌ **Update Position:** Move entities via drag-and-drop (updates X, Y coordinates).

## 4. Event Management
*   ✅✅ **Add Event:** Create a new narrative event.
*   ✅❌ **Edit Event:**
    *   Modify Name.
    *   Modify Description.
    *   Modify Importance level.
    *   Modify Position (X, Y coordinates).
    *   Modify Attributes (based on schema).
*   ✅❌ **Delete Event:** Remove an event from the current chapter.
*   ✅❌ **Update Position:** Move events via drag-and-drop (updates X, Y coordinates).

## 5. Relationship Management
*   ✅✅ **Add Relationship:** Create a link between two entities or events.
    *   *Properties:* Source UID, Target UID, Relationship Type (Agency, Causality, Sentiment, Chronotope, Possession, Location), Description.
*   ✅❌ **Edit Relationship:** Modify the source, target, type, or description of an existing relationship.
*   ✅✅ **Delete Relationship:** Remove a relationship from the current chapter.

## 6. Prose Management
*   ✅✅ **Edit Chapter Title:** Set the title for the current slot's prose.
*   ✅✅ **Edit Chapter Content:** Set the narrative text for the current slot.
*   ✅✅ **Save Prose:** Persist title and content to `Prose.json`.
*   ✅❌ **Analyze Prose (LLM):** Use an LLM to extract potential entities and events from the prose text.

## 7. Settings Management

### App Settings (Global)
*   ✅❌ **LLM Endpoint:** Set the URL for the LLM API (e.g., Ollama).
*   ✅❌ **LLM Model:** Set the model name to be used for generation and analysis.
*   ✅❌ **Snap to Grid:** Toggle whether entity positions should snap to a grid.
*   ✅❌ **Grid Size:** Set the size of the grid in pixels.

### Story Settings (Per Canvas)
*   ✅❌ **Importance Levels:**
    *   Add a new importance level.
    *   Edit the name of an existing level.
    *   Remove an importance level.

### Attribute Schemas (Per Canvas)
Define "recommended" or "required" attribute templates for each entity type (Actor, Place, Item, Knowledge, Event).
*   ✅❌ **Add Attribute Template:** Define a new attribute field.
    *   *Properties:* Name, Type (Text, Number, Select), Required flag.
    *   *Select Type:* Define options and toggle "Allow Custom" (to add new options during entity editing).
*   ✅❌ **Edit Attribute Template:** Modify properties of an existing template.
*   ✅❌ **Remove Attribute Template:** Delete a template from the schema.

## 8. Generators
*   ✅✅ **Generate Content:** Use procedural logic or an LLM to generate:
    *   Names
    *   Traits
    *   Characters
    *   Places
    *   Items
    *   Knowledge
    *   Events
*   ✅✅ **Custom Prompting:** Provide additional context to the generator.
*   ✅✅ **Save Generated Content:** Automatically create and save the generated entities/events into the current canvas.

# Upcoming Tasks

[ ] Go through functionality.md and implement all 'missing' features (I'll add it here) 
  *   ✅❌ **Edit Entity:**
    *   Modify Global Name (Identity).
    *   Modify Importance level.
    *   Modify Position (X, Y coordinates).
    *   Modify Attributes (based on schema).
    [ ] - CLI should be able to edit entities
  *   ✅❌ **Auto-Arrange:** Deterministically reposition all entities on the canvas based on type and importance.
    [ ] - CLI should be able to execute this function
  *   ✅❌ **Toggle Visibility:** Filter entities on the canvas by type.
    [X] - We don't have to implement this 
  *   ✅❌ **Update Position:** Move entities via drag-and-drop (updates X, Y coordinates).
    [ ] - It should be possible to edit these coordinates in the CLI, even if it will rarely be used

  *   ✅❌ **Edit Event:**
    *   Modify Name.
    *   Modify Description.
    *   Modify Importance level.
    *   Modify Position (X, Y coordinates).
    *   Modify Attributes (based on schema).
    [ ] - CLI should be able to edit events
  *   ✅❌ **Delete Relationship:** Remove a relationship from the current chapter.
    [ ] - CLI should be able to delete relationships
  *   ✅❌ **Delete Event:** Remove an event from the current chapter.
    [ ] - CLI should be able to delete events
  *   ✅❌ **Update Position:** Move events via drag-and-drop (updates X, Y coordinates).
    [ ] - CLI Should be able to event's position

  *   ✅❌ **Edit Relationship:** Modify the source, target, type, or description of an existing relationship. 
    [ ] - CLI should be able to edit relationships

  *   ✅❌ **Analyze Prose (LLM):** Use an LLM to extract potential entities and events from the prose text.
    [X] - Don't implement this now, because this feature is still very experimental.


  *   ✅❌ **LLM Endpoint:** Set the URL for the LLM API (e.g., Ollama).
  *   ✅❌ **LLM Model:** Set the model name to be used for generation and analysis.
  *   ✅❌ **Snap to Grid:** Toggle whether entity positions should snap to a grid.
  *   ✅❌ **Grid Size:** Set the size of the grid in pixels. 
    [ ] - CLI should be able to set all of these settings

  *   ✅❌ **Importance Levels:**
    [X] - Don't implement this, at the moment I'm not quite happy with the current GUI implementation

  *   ✅❌ **Add Attribute Template:** Define a new attribute field.
    *   *Properties:* Name, Type (Text, Number, Select), Required flag.
    *   *Select Type:* Define options and toggle "Allow Custom" (to add new options during entity editing).
  *   ✅❌ **Edit Attribute Template:** Modify properties of an existing template.
  *   ✅❌ **Remove Attribute Template:** Delete a template from the schema.
    [ ] - CLI should be able to add, edit and remove attribute for all the different entities


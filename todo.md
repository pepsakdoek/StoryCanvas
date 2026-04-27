# Things that we want to still implement

* Better settings. We must remember that we want this to be fully (or mostly) modular, so for each entity type (actors, places, items, knowledge, events, relationships) the user may want to add specific fields that may or may not be required, as well as it should have types like dropdowns, or 'text input' or number etc. 

* GUI grab the canvas to move it around (we started not 100% sure if this is implemented)

* An actual 'Prose' section where the user can write their chapters (how much 'richness' do we want to give the editor? I don't see this app as a 'formatter for books' it's just a way too keep thoughts together and develop a plot. But HTML / .md level of formatting would be nice. Maybe there is some sort of open source editor we can use?)

* Ability to link back to local LLM or cloud LLM.  The long term idea (at least for testing) is that I'll take an existing book and paste it in and see how the local or cloud LLM creates the objects.

* Time should have the ability to have 'sub' times. So a chapter is a great starting point, but even in a chapter one might want to split it into parts to 'flow' with the story better


# Implementation Notes

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

## Name Generator (`poc-tests/name-generator.py`)
- [x] Basic LLM integration (Ollama)
- [x] Fallback procedural generation
- [x] JSON validation with Pydantic
- [x] Generators for: Names, Traits, Character, Place, Item, Knowledge, Event
- [ ] **Event & Knowledge linking**
  - [ ] UI to select existing entity UUIDs for `involved_uids` (Event)
  - [ ] UI to select existing entity UUIDs for `location_uid` (Event)
  - [ ] UI to select existing entity UUIDs for `source_uid`/`target_uid` (Relationships)
  - [ ] Support recursive Events as sources (Event → Event)
- [ ] **Batch generation**: Allow generating multiple entities/events in one call
- [ ] **Import to active canvas**: Add "Save to Canvas" button to push generated JSON into current slot

## Future Enhancements
- [ ] Support for Gemini API (cloud) alongside Ollama
- [ ] History panel to review previous generations
- [ ] Export to JSON/CSV
- [ ] Prompt templates library
- [ ] Multi-turn chat mode for iterative refinement

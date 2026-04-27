# Implementation Notes

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

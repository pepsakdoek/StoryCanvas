# Things that we want to still implement
  [ ] Random name / entity generator.  
  [ ] Clicking on the canvas should enable select area, so we can delete many at once (it's really only useful for deletes)
  [ ] Keyboard shortcuts
  [ ] Implement the 'importance' filter
  [ ] The current 'tick box' filters at the top doesnt really make sense I think.
  [ ] Time should have the ability to have 'sub' times. So a chapter is a great starting point, but even in a chapter one might want to split it into parts to 'flow' with the story better
  [ ] Local / cloud LLM to take a piece of text and create the objects for it (cli), we'll need to generate a system prompt

# CLI Feature Parity (Missing Functionality)
  [ ] **Canvas Management**
    - [ ] Auto-Arrange entities via CLI command.
  [ ] **Entity Management**
    - [ ] Edit existing entities (Name, Importance, Attributes, Coordinates).
    - [ ] Filtered listing (e.g., list only Actors, list only Places).
  [ ] **Event Management**
    - [ ] Edit existing events (Name, Description, Importance, Attributes, Coordinates).
  [ ] **Relationship Management**
    - [ ] Edit existing relationships (Source, Target, Type, Description).
  [ ] **Prose Management**
    - [ ] Analyze Prose via LLM to extract entities/events (CLI implementation of `analyze_prose`).
  [ ] **Settings Management**
    - [ ] Edit App Settings (LLM Endpoint, Model, Grid/Snap settings).
    - [ ] Edit Story Settings (Importance Levels).
    - [ ] Edit Attribute Schemas (Add/Edit/Remove attribute templates for different entity types).
  [ ] **Generators**
    - [ ] Better handling of 'Traits' generation results (e.g., allow applying them to an entity).

# Implementation Notes

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

[ ] Random generator
  [ ] Needs to be enabled on most UI's
  [ ] Should be able to link to major LLMs too if not self hosted
  [ ] Some types of random things needs more uuid context. This might become the main 'feature' of the tool.
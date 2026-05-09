# Things that we want to still implement
  [ ] Expand events - how is an event structured? How does it differ from a beat?
  [ ] Random name / entity generator - this should be on every property.
  [ ] Clicking on the canvas should enable select area, so we can delete many at once (it's really only useful for deletes)
  [x] Keyboard shortcuts
  [x] Implement the 'importance' filter
  [x] The current 'tick box' filters at the top doesnt really make sense I think.
  [ ] Local / cloud LLM to take a piece of text and create the objects for it (cli), we'll need to generate a system prompt
    [ ] This sort of exist, but it's not at all 'good' at the moment - but I don't think it needs to be yet. Focus should rather be on the name / entity / attribute generator.

# Implementation Notes

Todo Item: Keyboard Shortcuts. 
- `Ctrl + PgUp / PgDn`: Traverses through beats (timeline movement).
- `Ctrl + Shift + PgUp / PgDn`: Chapter (Slot) switching.
- **Beat Trigger:** 4 consecutive newlines in the rich editor triggers an immediate save and "commits" the current text block as narrative beats.

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

[ ] Random generator
  [ ] Needs to be enabled on most UI's
  [ ] Should be able to link to major LLMs too if not self hosted
  [ ] Some types of random things needs more uuid context. This might become the main 'feature' of the tool.
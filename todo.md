# Things that we want to still implement
  [ ] Random name / entity generator.  
  [ ] Clicking on the canvas should enable select area, so we can delete many at once (it's really only useful for deletes)
  [ ] Keyboard shortcuts
  [ ] Implement the 'importance' filter
  [ ] The current 'tick box' filters at the top doesnt really make sense I think.
  [ ] Time should have the ability to have 'sub' times. So a chapter is a great starting point, but even in a chapter one might want to split it into parts to 'flow' with the story better
  [ ] Prose Editor Fixes:
    [ ] First analuse if any of these issues are our fault and how many is the library. Do not try to fix things that are library issues.
    [ ] UI: The 'rich' edit options are hidden by the chapter toolbar. The hovering header bar is cool, but perhaps we should ditch it so elements can fit neatly.
    [ ] Bug: Fix Enter key adding newline but not moving the cursor
    [ ] Bug: Fix first character becoming last character when starting with a blank area (e.g., "Mary" -> "aryM") - this might be related to the proposed improvement below
    [ ] Improvement: Debounce or optimize auto-save to prevent cursor jumping during typing
  [ ] Local / cloud LLM to take a piece of text and create the objects for it (cli), we'll need to generate a system prompt



# Implementation Notes

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

[ ] Random generator
  [ ] Needs to be enabled on most UI's
  [ ] Should be able to link to major LLMs too if not self hosted
  [ ] Some types of random things needs more uuid context. This might become the main 'feature' of the tool.
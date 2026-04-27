# Things that we want to still implement

[ ] In Settings: 
  [ ] We have the add attribute button but it doesn't work at the moment
  [ ] 'Select' inputs must bring up sub menu to add options
  
[ ] GUI 
  [ ] grab the canvas to move it around
     [ ] Space changes the icon to a hand, but it doesn't drag the icons around
  [X] Icons should give what it is on hover
  [ ] Clicking on the canvas should enable select area, so we can delete many at once (it's really only useful for deletes)
  [ ] Keyboard shortcuts
  [ ] Prose Editor Fixes:
    [ ] UI: Make prose area go down to the bottom of the screen with an independent scroll bar
    [ ] Bug: Fix first character becoming last character when starting with a blank area (e.g., "Mary" -> "aryM")
    [ ] Bug: Fix Enter key adding newline but not moving the cursor
    [ ] Improvement: Debounce or optimize auto-save to prevent cursor jumping during typing


[X] An actual 'Prose' section where the user can write their chapters (Implemented using Quill/ui.editor for lightweight WYSIWYG, optimized for space)

[X] Ability to link back to local LLM or cloud LLM inside the Prose to. (Implemented "Extract Entities" button for LLM analysis of prose)

[ ] Time should have the ability to have 'sub' times. So a chapter is a great starting point, but even in a chapter one might want to split it into parts to 'flow' with the story better


# Implementation Notes

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

[ ] Random generator
  [ ] Needs to be enabled on most UI's
  [ ] Should be able to link to major LLMs too if not self hosted
  [ ] Some types of random things needs more uuid context. This might become the main 'feature' of the tool.
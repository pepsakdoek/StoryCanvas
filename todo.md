# Things that we want to still implement

[ ] In Settings: 
  [ ] We have the add attribute button but it doesn't work at the moment
  [ ] 'Select' inputs must bring up sub menu to add options
  
[ ] GUI 
  [ ] grab the canvas to move it around
     [ ] Space changes the icon to a hand, but it doesn't drag the icons around
  [ ] Icons should give what it is on hover
  [ ] Clicking on the canvas should enable select area, so we can delete many at once (it's really only useful for deletes)
  [ ] Keyboard shortcuts


[ ] An actual 'Prose' section where the user can write their chapters (how much 'richness' do we want to give the editor? I don't see this app as a 'formatter for books' it's just a way too keep thoughts together and develop a plot. But HTML / .md level of formatting would be nice. Maybe there is some sort of open source editor we can use?)

[X] Ability to link back to local LLM or cloud LLM inside the Prose to.  The long term idea (at least for testing) is that I'll take an existing book and paste it in and see how the local or cloud LLM creates the objects. (Sort of implemented)

[ ] Time should have the ability to have 'sub' times. So a chapter is a great starting point, but even in a chapter one might want to split it into parts to 'flow' with the story better


# Implementation Notes

Todo Item: Random name / entity generator. This should be very customisable and probably linked to an LLM.  Certain 'civs' might have different types of names

[ ] Random generator
  [ ] Needs to be enabled on most UI's
  [ ] Should be able to link to major LLMs too if not self hosted
  [ ] Some types of random things needs more uuid context. This might become the main 'feature' of the tool.
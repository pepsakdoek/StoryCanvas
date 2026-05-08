# Narrative Beats

In StoryCanvas, prose is not stored as a single block of text. Instead, it is broken down into discrete units called **Beats**.

## What is a Beat?
A Beat is the smallest sensible unit of narrative context. It acts as a coordinate in your story's timeline, allowing you to anchor characters, events, and relationship changes to specific moments in the text.

### Guidelines for Beats:
*   **Size:** A beat is typically **one or two paragraphs** long.
*   **Context:** It should contain a self-contained action, description, or piece of dialogue.
*   **Dialogue:** An entire conversation between characters can usually fall into a single beat. 
*   **When to Split:** You should split a beat if a significant change occurs *mid-scene*. For example, if two characters start a conversation as friends but end it as enemies, the moment the relationship shifts should be the start of a new beat.
*   **Indexing:** Similar to Biblical indexing (Book:Chapter:Verse), beats allow the engine to track the state of the world at any specific "Verse" in the story.

## For LLMs
When analyzing or generating story text, treat each Beat as a state-change opportunity. 
*   **Extraction:** When extracting entities, note which Beat UID they first appear in.
*   **Generation:** When generating new prose, aim to produce logical Beats that can be indexed and tracked.

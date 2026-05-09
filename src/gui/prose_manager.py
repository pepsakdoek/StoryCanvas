import json
import re
from typing import List, Optional
from nicegui import ui, run
from ..models import Beat, Prose

class ProseManager:
    def __init__(self, gui):
        self.gui = gui
        self.state = None
        self.editor: Optional[ui.editor] = None
        self.save_timer: Optional[ui.timer] = None
        self.char_count_label = None

    def build_panel(self):
        self.state = self.gui.state
        if not self.state: return

        with ui.column().classes('w-full h-full p-0 gap-0 overflow-hidden bg-white').props('id=prose-inner-container'):
            # Header
            with ui.row().classes('w-full items-center gap-2 border-b border-slate-200 p-2'):
                ui.icon('edit_note').classes('text-slate-400')
                self.title_input = ui.input(value=self.state.prose.title, placeholder='Chapter Title') \
                    .classes('grow text-sm').props('dense borderless').on('change', self.save_prose)
                with ui.row().classes('gap-1'):
                    ui.button(icon='auto_awesome', on_click=self.prose_llm_action).props('flat dense round color=amber-7').tooltip('Extract Entities (LLM)')
                    ui.button(icon='save', on_click=lambda: self.save_prose(notify=True)).props('flat dense round color=blue-5').tooltip('Save')
            
            # Unified Rich Editor
            # We join beats with a special marker tag: <span class="beat-marker" data-idx="..."><sup>N</sup></span>
            content = self._beats_to_html(self.state.prose.beats)
            
            self.editor = ui.editor(value=content).classes('w-full flex-1 text-sm overflow-auto').props('id=prose-editor')
            self.editor.props('flat square dense toolbar-rounded toolbar-bg=blue-grey-1 paragraph-tag=p')
            
            self.editor.on_value_change(self.handle_change)
            # Custom key handler for Ctrl+Enter within the editor context
            self.editor.on('keydown.control.enter', self.handle_ctrl_enter)

            with ui.row().classes('w-full justify-between items-center px-2 py-1 bg-slate-50 border-t border-slate-100'):
                ui.label('Unified Storyboard Editor').classes('text-[10px] text-slate-400 uppercase font-bold tracking-tighter')
                self.char_count_label = ui.label(f'Chars: {len(content)}').classes('text-[10px] text-slate-400 font-mono')

    def _beats_to_html(self, beats: List[Beat]) -> str:
        html_parts = []
        for i, b in enumerate(beats):
            # We wrap the text in a way that helps us split it back later
            # Note: We use a distinct marker. 
            marker = f'<span class="beat-marker" contenteditable="false" style="color: #3b82f6; font-weight: bold; margin-right: 4px; user-select: none;"><sup>{i+1}</sup></span>'
            # If the beat text doesn't start with a tag, wrap it in a <p>
            text = b.text.strip()
            if not text.startswith('<'):
                text = f'<p>{text}</p>'
            
            # Inject marker into the first paragraph
            if text.startswith('<p>'):
                text = text.replace('<p>', f'<p>{marker}', 1)
            else:
                text = f'{marker}{text}'
            
            html_parts.append(text)
        
        return "".join(html_parts)

    def handle_change(self, e):
        if self.char_count_label:
            self.char_count_label.text = f'Chars: {len(e.value or "")}'
        
        if self.save_timer:
            self.save_timer.cancel()
        self.save_timer = ui.timer(2.0, self.save_prose, once=True)

    def handle_ctrl_enter(self):
        """Insert a new beat marker at cursor and trigger state inheritance."""
        # This is tricky with ui.editor. We'll use JS to insert the marker and a newline.
        next_idx = len(self.state.prose.beats) + 1
        marker_html = f'<span class="beat-marker" contenteditable="false" style="color: #3b82f6; font-weight: bold; margin-right: 4px; user-select: none;"><sup>{next_idx}</sup></span>'
        
        # 1. Split logic: Save current state first
        self.save_prose()
        
        # 2. Use JS to insert at cursor
        js = f"""
            var editor = document.getElementById('prose-editor');
            var quill = Quill.find(editor.querySelector('.q-editor__content'));
            var range = quill.getSelection();
            if (range) {{
                quill.insertText(range.index, '\\n', 'user');
                quill.clipboard.dangerouslyPasteHTML(range.index + 1, '{marker_html}&nbsp;', 'user');
                quill.setSelection(range.index + 2);
            }}
        """
        ui.run_javascript(js)
        
        # 3. Create the data-side beat with inheritance
        # We find which beat the cursor was in (approximate) or just append
        # For simplicity in this 'unified' mode, Ctrl+Enter always creates a NEW beat at the END
        # unless we do complex DOM mapping. Let's stick to 'Add Beat' logic for now.
        new_idx = self.gui.state.create_next_beat(len(self.gui.state.prose.beats) - 1)
        self.gui.state.set_active_beat(new_idx)
        self.gui._refresh_timeline()
        ui.notify(f"Beat {new_idx+1} started. State inherited.", type='positive', position='top-right')

    def save_prose(self, notify=False):
        if not self.gui.state: return
        self.gui.state.prose.title = self.title_input.value
        
        raw_html = self.editor.value
        # Parse HTML back into beats
        # We split by the beat-marker spans
        parts = re.split(r'<span class="beat-marker".*?</span>', raw_html)
        # The first part is usually empty or preamble before the first beat
        parts = [p.strip() for p in parts if p.strip()]
        
        # Update beats list
        # If the number of beats changed, we need to be careful with states
        current_beats = self.gui.state.prose.beats
        new_beats = []
        
        for i, text in enumerate(parts):
            if i < len(current_beats):
                # Update existing beat text
                beat = current_beats[i]
                beat.text = text
                new_beats.append(beat)
            else:
                # Create new beat (should inherit from previous)
                from ..models import Beat
                prev_beat = new_beats[-1] if new_beats else None
                if prev_beat:
                    # Inherit state
                    states = {uid: s.model_dump() for uid, s in prev_beat.entity_states.items()}
                    rels = [r.model_dump() for r in prev_beat.relationships]
                    new_beats.append(Beat(text=text, entity_states=states, relationships=rels))
                else:
                    new_beats.append(Beat(text=text))
        
        self.gui.state.prose.beats = new_beats
        self.gui.state.save_prose(self.gui.state.prose)
        
        if notify:
            ui.notify("Prose saved!", type='positive', position='top')
        self.save_timer = None
        self.gui._refresh_timeline()

    def focus_beat(self, index: int):
        """Scroll to and highlight the N-th beat marker in the unified editor."""
        js = f"""
            var editor = document.getElementById('prose-editor');
            if (editor) {{
                var markers = editor.querySelectorAll('.beat-marker');
                if (markers.length > {index}) {{
                    markers[{index}].scrollIntoView({{behavior: 'smooth', block: 'center'}});
                    // Add a brief glow effect to the marker
                    var marker = markers[{index}];
                    marker.style.transition = 'all 0.5s';
                    marker.style.textShadow = '0 0 10px #3b82f6';
                    marker.style.transform = 'scale(1.5)';
                    setTimeout(() => {{
                        marker.style.textShadow = 'none';
                        marker.style.transform = 'scale(1.0)';
                    }}, 2000);
                }}
            }}
        """
        ui.run_javascript(js)

    async def prose_llm_action(self):
        content = self.editor.value
        if not content or len(content) < 10:
            ui.notify("Prose too short", type='warning')
            return
            
        from ..generators import analyze_prose
        ui.notify("Analyzing with LLM...", type='ongoing', spinner=True)
        
        # Strip markers for the LLM
        clean_text = re.sub('<[^<]+?>', '', content)
        
        result = await run.io_bound(analyze_prose,
            clean_text,
            self.gui.state.app_settings.llm_endpoint,
            self.gui.state.app_settings.llm_model
        )
        
        if result:
            with ui.dialog() as dialog, ui.card().classes('w-[600px]'):
                ui.label('Analysis').classes('text-h6 font-bold')
                ui.markdown(result).classes('w-full max-h-96 overflow-y-auto p-4 bg-slate-50 rounded')
                ui.button('Close', on_click=dialog.close).props('flat')
            dialog.open()
        else:
            ui.notify("LLM failed", type='negative')

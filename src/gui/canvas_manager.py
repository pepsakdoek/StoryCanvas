import math
from nicegui import ui
from ..models import EntityIdentity, EntityState, Event, Relationship, RelationshipType

class CanvasManager:
    def __init__(self, gui):
        self.gui = gui

    def refresh_canvas_content(self):
        if not self.gui.canvas_container: return
        self.gui.canvas_container.clear()
        with self.gui.canvas_container:
            ui.element('div').classes('grid-overlay')
            self._draw_relationships()
            
            for uid, state in self.gui.state.entity_states.items():
                identity = self.gui.state.registry.entities.get(uid)
                if not identity or not self.gui.type_filter.get(identity.entity_type, True): continue
                if identity.entity_type == 'Actor' and not self.gui.importance_filter.get(identity.importance, True): continue
                self._add_entity_to_ui(identity, state, f"entity-{identity.entity_type.lower()}")
            
            if self.gui.type_filter.get('Event', True):
                for ev in self.gui.state.events:
                    self._add_event_to_ui(ev)

    def _add_entity_to_ui(self, identity: EntityIdentity, state: EntityState, css_class: str):
        card = ui.card().classes(f'entity-block p-0 {css_class}').style(f'left: {state.x}px; top: {state.y}px')
        with card:
            ui.label(identity.name).classes('font-bold mt-1')
            if identity.entity_type == 'Actor':
                ui.label(identity.importance).classes('text-[10px] uppercase text-slate-400')
            with ui.context_menu():
                ui.menu_item('Edit', on_click=lambda: self.gui.dialogs.edit_entity_dialog(identity, state))
                ui.menu_item('Delete from Slot', on_click=lambda: self.gui._delete_entity(identity.uid))
        card.on('mousedown', lambda e: self.gui._handle_mousedown(e, card, identity.uid, False))
        card.on('dblclick', lambda: self.gui.dialogs.edit_entity_dialog(identity, state))

    def _add_event_to_ui(self, ev: Event):
        card = ui.card().classes('entity-block entity-event p-2').style(f'left: {ev.x}px; top: {ev.y}px')
        with card:
            ui.label(ev.name).classes('font-bold text-center')
            ui.icon('bolt').classes('text-slate-400')
            with ui.context_menu():
                ui.menu_item('Edit Event', on_click=lambda: self.gui.dialogs.edit_event_dialog(ev))
                ui.menu_item('Delete Event', on_click=lambda: self.gui._delete_event(ev.uid))
        card.on('mousedown', lambda e: self.gui._handle_mousedown(e, card, ev.uid, True))
        card.on('dblclick', lambda: self.gui.dialogs.edit_event_dialog(ev))

    def _get_intersection_offset(self, ux, uy, is_event):
        if is_event: return 52 
        w, h = 60, 40
        if abs(ux) * h > abs(uy) * w:
            return abs(w / ux) if ux != 0 else h
        else:
            return abs(h / uy) if uy != 0 else w

    def _draw_relationships(self):
        links = {}
        for rel in self.gui.state.relationships:
            pair = tuple(sorted([rel.source_uid, rel.target_uid]))
            links[pair] = links.get(pair, 0) + 1

        for rel in self.gui.state.relationships:
            src_state = self.gui.state.entity_states.get(rel.source_uid)
            dst_state = self.gui.state.entity_states.get(rel.target_uid)
            is_src_ev = False
            if not src_state:
                src_state = next((ev for ev in self.gui.state.events if ev.uid == rel.source_uid), None)
                is_src_ev = True
            is_dst_ev = False
            if not dst_state:
                dst_state = next((ev for ev in self.gui.state.events if ev.uid == rel.target_uid), None)
                is_dst_ev = True

            if src_state and dst_state:
                x1, y1 = src_state.x + (50 if is_src_ev else 60), src_state.y + (50 if is_src_ev else 40)
                x2, y2 = dst_state.x + (50 if is_dst_ev else 60), dst_state.y + (50 if is_dst_ev else 40)
                dx, dy = x2 - x1, y2 - y1
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < 20: continue
                ux, uy = dx/dist, dy/dist

                pair = tuple(sorted([rel.source_uid, rel.target_uid]))
                is_bidir = links[pair] > 1
                
                # Perpendicular vector for bidirectional separation
                # We use source order to ensure they push in opposite directions
                # A->B gets +20, B->A gets -20 relative to its own vector
                # But since the vector for B->A is already negative of A->B,
                # just using a fixed offset relative to its OWN vector works naturally.
                off_mag = 20 if is_bidir else 0
                px, py = -uy * off_mag, ux * off_mag
                
                # Dynamic edge detection
                s_off = self._get_intersection_offset(ux, uy, is_src_ev) + 2
                e_off = self._get_intersection_offset(-ux, -uy, is_dst_ev) + 2
                
                lx1, ly1 = x1 + ux * s_off + px/2, y1 + uy * s_off + py/2
                lx2, ly2 = x2 - ux * e_off + px/2, y2 - uy * e_off + py/2
                
                ldx, ldy = lx2 - lx1, ly2 - ly1
                ldist = math.sqrt(ldx**2 + ldy**2)
                angle = math.atan2(ldy, ldx) * 180 / math.pi
                
                # Draw the line
                ui.element('div').classes('relationship-line').style(
                    f'left: {lx1}px; top: {ly1}px; width: {ldist}px; transform: rotate({angle}deg)'
                )
                
                # Label at midpoint + perpendicular offset
                mid_x, mid_y = (lx1 + lx2) / 2, (ly1 + ly2) / 2
                # Additional label offset to clear the line
                label_x, label_y = mid_x + px/1.5, mid_y + py/1.5
                
                label_cont = ui.element('div').classes('relationship-label').style(f'left: {label_x}px; top: {label_y}px')
                with label_cont:
                    ui.label(rel.description)
                    with ui.context_menu():
                        ui.menu_item('Edit Link', on_click=lambda r=rel: self.gui.dialogs.edit_relationship_dialog(r))
                        ui.menu_item('Delete Link', on_click=lambda r=rel: self.gui._delete_relationship(r.uid))
                label_cont.on('dblclick', lambda r=rel: self.gui.dialogs.edit_relationship_dialog(r))

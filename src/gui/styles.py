from nicegui import ui

STYLE_DEFINITION = '''
<style>
    body { overflow: hidden; }
    .canvas-container {
        width: 100vw; height: 100vh;
        background-color: #f0f4f8;
        position: relative; overflow: hidden;
    }
    .canvas-content {
        position: absolute; top: 0; left: 0;
        width: 100%; height: 100%;
        transform-origin: 0 0;
    }
    .cursor-grab { cursor: grab !important; }
    .cursor-grabbing { cursor: grabbing !important; }
    .grid-overlay {
        position: absolute; top: 0; left: 0;
        width: 10000px; height: 10000px;
        background-image: 
            linear-gradient(to right, rgba(0, 0, 0, 0.05) 1px, transparent 1px),
            linear-gradient(to bottom, rgba(0, 0, 0, 0.05) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none; z-index: 0;
    }
    .entity-block {
        width: 120px; min-height: 80px;
        background-color: #ffffff;
        border: 2px solid #94a3b8;
        border-radius: 12px;
        display: flex; flex-direction: column;
        align-items: center; justify-content: center;
        text-align: center; position: absolute;
        cursor: move; z-index: 10;
        font-size: 0.85rem; padding: 8px;
        user-select: none;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
    }
    .entity-actor { border-left: 6px solid #ef4444; }
    .entity-place { border-left: 6px solid #22c55e; }
    .entity-item { border-left: 6px solid #eab308; }
    .entity-knowledge { border-left: 6px solid #a855f7; }
    .entity-event { border: 2px dashed #64748b; border-radius: 50%; width: 100px; height: 100px; background-color: #f1f5f9; }
    
    .relationship-line {
        position: absolute; height: 2px;
        background-color: #94a3b8;
        transform-origin: top left;
        pointer-events: none; z-index: 5;
        opacity: 0.6;
    }
    .relationship-line::after {
        content: '';
        position: absolute;
        right: -2px;
        top: -4px;
        border-top: 5px solid transparent;
        border-bottom: 5px solid transparent;
        border-left: 8px solid #94a3b8;
    }
    .relationship-label {
        position: absolute;
        font-size: 10px;
        font-weight: bold;
        background-color: rgba(255, 255, 255, 0.9);
        padding: 2px 8px;
        border-radius: 10px;
        border: 1px solid #cbd5e1;
        color: #475569;
        cursor: pointer;
        z-index: 20;
        white-space: nowrap;
        transform: translate(-50%, -50%);
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .relationship-label:hover {
        background-color: #f8fafc;
        border-color: #3b82f6;
        z-index: 25;
    }
    
    .header-bar {
        position: absolute; top: 16px; left: 16px; right: 16px;
        z-index: 50; height: 56px;
        background-color: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border-radius: 12px;
        padding: 0 16px;
        box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
        border: 1px solid rgba(0,0,0,0.05);
        display: flex; align-items: center; justify-content: space-between;
    }
    .slot-bubble {
        width: 24px; height: 24px; border-radius: 6px;
        background-color: #e2e8f0; cursor: pointer;
        display: flex; align-items: center; justify-content: center;
        font-size: 10px; font-weight: bold; color: #64748b;
        transition: all 0.2s;
    }
    .slot-bubble:hover { background-color: #cbd5e1; }
    .slot-bubble.active { background-color: #3b82f6; color: white; transform: scale(1.1); }
</style>
'''

def setup_styles():
    ui.add_head_html(STYLE_DEFINITION)

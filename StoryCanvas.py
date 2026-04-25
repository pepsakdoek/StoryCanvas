import argparse
from src.cli import run_cli
from src.gui import run_gui

def main():
    parser = argparse.ArgumentParser(description="Bard: Blank Canvas Narrative Engine")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()

if __name__ in {"__main__", "__mp_main__"}:
    main()

import argparse
import sys
import datetime
import os
from src.cli import run_cli
from src.gui import run_gui

def setup_logging():
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"output{timestamp}.log")
    
    # Simple tee implementation to log to both file and console
    class Tee:
        def __init__(self, file, stream):
            self.file = file
            self.stream = stream

        def write(self, data):
            self.file.write(data)
            self.stream.write(data)
            self.file.flush()

        def flush(self):
            self.file.flush()
            self.stream.flush()

        def isatty(self):
            return self.stream.isatty()

        @property
        def encoding(self):
            return self.stream.encoding

        @property
        def errors(self):
            return self.stream.errors

        @property
        def newline(self):
            return getattr(self.stream, 'newline', None)

    f = open(log_file, "w", encoding="utf-8")
    sys.stdout = Tee(f, sys.stdout)
    sys.stderr = Tee(f, sys.stderr)
    print(f"Logging to {log_file}")

def main():
    setup_logging()
    
    parser = argparse.ArgumentParser(description="StoryCanvas: Blank Canvas Narrative Engine")
    parser.add_argument("--cli", action="store_true", help="Run in CLI mode")
    args = parser.parse_args()

    if args.cli:
        run_cli()
    else:
        run_gui()

if __name__ in {"__main__", "__mp_main__"}:
    main()

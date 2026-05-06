import argparse
import sys
import datetime
import os
from src.cli import run_cli
from src.gui import run_gui 

import logging

# --- Logging Configuration ---
# Hierarchy (Most Verbose to Least): 
# logging.DEBUG (All) -> logging.INFO -> logging.WARNING -> logging.ERROR -> logging.CRITICAL
# Set to None to disable logging entirely.
GLOBAL_LOG_LEVEL = logging.DEBUG 
# -----------------------------

def setup_logging():
    if GLOBAL_LOG_LEVEL is None:
        logging.disable(logging.CRITICAL)
        return

    # Create logs directory if it doesn't exist
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"output{timestamp}.log")
    
    # Configure logging
    logging.basicConfig(
        level=GLOBAL_LOG_LEVEL,
        format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Redirect stdout and stderr to the logger
    class LoggerWriter:
        def __init__(self, level, original_stream):
            self.level = level
            self.original_stream = original_stream

        def write(self, message):
            if message.strip():
                self.level(message.strip())

        def flush(self):
            self.original_stream.flush()

        def isatty(self):
            return self.original_stream.isatty()

        @property
        def encoding(self):
            return self.original_stream.encoding

        @property
        def errors(self):
            return self.original_stream.errors

    # We don't want to infinite loop, so we only redirect if we are careful.
    # Actually, a better way to capture stdout/stderr is to use a custom handler or just rely on print() 
    # being used sparingly and logging used for everything else.
    
    logger = logging.getLogger("System")
    sys.stdout = LoggerWriter(logger.info, sys.stdout)
    sys.stderr = LoggerWriter(logger.error, sys.stderr)

    logging.info(f"Logging initialized. Level: DEBUG. File: {log_file}")

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

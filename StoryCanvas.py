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
    if getattr(setup_logging, "_initialized", False):
        return
    setup_logging._initialized = True

    if GLOBAL_LOG_LEVEL is None:
        logging.disable(logging.CRITICAL)
        return

    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # Restore datestamped filename as requested
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = os.path.join(log_dir, f"output{timestamp}.log")
    
    # Store original streams
    original_stdout = sys.stdout
    original_stderr = sys.stderr

    # Configure root logger
    logger = logging.getLogger()
    logger.setLevel(GLOBAL_LOG_LEVEL)
    logger.handlers = []

    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s')

    fh = logging.FileHandler(log_file, encoding='utf-8', mode='w')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    ch = logging.StreamHandler(original_stdout)
    ch.setFormatter(formatter)
    logger.addHandler(ch)
    
    class LoggerWriter:
        def __init__(self, log_func, original_stream):
            self.log_func = log_func
            self.original_stream = original_stream
            self._lock = False # Simple re-entry guard

        def write(self, message):
            if self._lock:
                self.original_stream.write(message)
                return
            
            if message.strip():
                self._lock = True
                try:
                    self.log_func(message.strip())
                finally:
                    self._lock = False

        def flush(self):
            self.original_stream.flush()

        def isatty(self):
            return self.original_stream.isatty()

    sys.stdout = LoggerWriter(logging.getLogger("STDOUT").info, original_stdout)
    sys.stderr = LoggerWriter(logging.getLogger("STDERR").error, original_stderr)

    logging.info(f"Logging initialized. Level: {logging.getLevelName(GLOBAL_LOG_LEVEL)}. File: {log_file}")

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

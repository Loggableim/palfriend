"""
PalFriend Launcher - Windows Executable Entry Point

This launcher provides a simple entry point for the Windows executable.
It starts the PalFriend web interface automatically.
"""

import sys
import os
import logging
import webbrowser
import time
from threading import Timer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)
log = logging.getLogger("PalFriend-Launcher")


def open_browser(url: str, delay: float = 2.0):
    """
    Open browser after a delay to allow the server to start.
    
    Args:
        url: URL to open
        delay: Delay in seconds before opening browser
    """
    def _open():
        try:
            log.info(f"Opening browser to {url}")
            webbrowser.open(url)
        except Exception as e:
            log.error(f"Failed to open browser: {e}")
    
    Timer(delay, _open).start()


def main():
    """
    Main launcher entry point.
    Starts the PalFriend web interface.
    """
    log.info("=" * 50)
    log.info("PalFriend Launcher")
    log.info("=" * 50)
    log.info("")
    
    # Import app module
    try:
        from app import main as app_main
        
        # Get port from environment variable (same as app.py)
        port = int(os.environ.get('PORT', 5008))
        url = f"http://localhost:{port}"
        log.info(f"Starting PalFriend web interface on {url}")
        open_browser(url, delay=3.0)
        
        # Start the Flask app
        app_main()
        
    except KeyboardInterrupt:
        log.info("\nShutting down PalFriend...")
        sys.exit(0)
    except Exception as e:
        log.error(f"Failed to start PalFriend: {e}")
        log.error("Please check that all dependencies are installed.")
        
        # On Windows, keep the window open to show the error
        if sys.platform == "win32":
            input("\nPress Enter to exit...")
        
        sys.exit(1)


if __name__ == "__main__":
    main()

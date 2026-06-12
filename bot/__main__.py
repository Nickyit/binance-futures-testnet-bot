"""
Allow running the bot package as a module:
    python -m bot --symbol BTCUSDT --side BUY --type MARKET --quantity 0.01
"""

import sys
import os

# Ensure the project root is on sys.path so imports resolve correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from cli import main  # noqa: E402

if __name__ == "__main__":
    main()

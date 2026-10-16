"""Agent-neutral entry point for the standalone character toolkit (Python 3.11+)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from builder.cli import main

if __name__ == '__main__':
    main()

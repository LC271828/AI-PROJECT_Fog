"""Pytest config for experiments-only tests.

Adds the project root to sys.path so tests here can import `experiments.*` and `src.*` if needed.
This test suite is opt-in and not executed by CI (CI runs only top-level tests/).
"""
from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

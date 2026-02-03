"""Pytest configuration for SQL agent tests."""

import sys
from pathlib import Path

# Ensure sql-agent root is on path
_sql_agent_root = Path(__file__).resolve().parent.parent
if str(_sql_agent_root) not in sys.path:
    sys.path.insert(0, str(_sql_agent_root))

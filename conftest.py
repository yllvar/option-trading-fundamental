"""
Pytest configuration file.
Sets up paths and fixtures for testing.
"""

import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Also add subdirectories
for subdir in ['options', 'portfolio', 'factors', 'utils']:
    sys.path.insert(0, str(project_root / subdir))

"""
Cloud Function entry point
Imports and exposes the HTTP function from fred module
"""
import sys
from pathlib import Path

# Add current directory to path
current_dir = Path(__file__).parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

# Import the actual function
from fred.main import ingest_fred_http

# Expose it at module level for Cloud Functions
__all__ = ['ingest_fred_http']

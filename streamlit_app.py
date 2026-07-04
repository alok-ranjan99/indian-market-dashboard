"""Deployment entrypoint for Streamlit Community Cloud.

Kept thin on purpose — all logic lives in the `imd` package under src/.
"""

import sys
from pathlib import Path

# Make the src/ layout importable both locally and on Streamlit Cloud.
sys.path.insert(0, str(Path(__file__).parent / "src"))

from imd.ui.app import main  # noqa: E402

if __name__ == "__main__":
    main()

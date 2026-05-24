import sys
from pathlib import Path
import os
import tempfile


BACKEND_ROOT = Path(__file__).resolve().parents[2]
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

TEST_DB_PATH = Path(tempfile.gettempdir()) / "phishguard_test.db"
os.environ["PHISHGUARD_DB_PATH"] = str(TEST_DB_PATH)

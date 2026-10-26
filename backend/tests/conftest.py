import os
from pathlib import Path
import secrets


os.environ["DATABASE_PATH"] = str(Path(__file__).with_name("test.sqlite3"))
os.environ["TEST_PASSWORD"] = secrets.token_urlsafe(16)
os.environ["TEST_WRONG_PASSWORD"] = secrets.token_urlsafe(16)

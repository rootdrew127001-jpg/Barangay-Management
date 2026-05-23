import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATABASE_URL = f"sqlite:///{BASE_DIR}/database.sqlite"
SECRET_KEY = "dev-secret-key-change-in-production"

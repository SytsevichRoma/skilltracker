import os

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    DB_PATH = os.path.join(BASE_DIR, "skilltracker.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ i18n
    BABEL_DEFAULT_LOCALE = "uk"
    LANGUAGES = ["uk", "en", "pl", "de", "es"]

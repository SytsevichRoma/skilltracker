import os

try:
    from dotenv import load_dotenv
except ImportError:  # optional for environments that already load env vars
    load_dotenv = None

BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))

if load_dotenv:
    load_dotenv(os.path.join(BASE_DIR, ".env"), override=False)

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key")

    DB_PATH = os.path.join(BASE_DIR, "skilltracker.db")
    SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL", f"sqlite:///{DB_PATH}")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # ✅ i18n
    BABEL_DEFAULT_LOCALE = "uk"
    LANGUAGES = ["uk", "en", "pl", "de", "es"]

    # ✅ Fondy payments
    FONDY_MERCHANT_ID = os.environ.get("FONDY_MERCHANT_ID")
    FONDY_SECRET_KEY = os.environ.get("FONDY_SECRET_KEY")
    FONDY_API_URL = os.environ.get("FONDY_API_URL", "https://pay.fondy.eu/api/checkout/url")
    PRO_AMOUNT = int(os.environ.get("PRO_AMOUNT", "49900"))
    PRO_CURRENCY = os.environ.get("PRO_CURRENCY", "UAH")
    PRO_DURATION_DAYS = int(os.environ.get("PRO_DURATION_DAYS", "30"))
    BILLING_PROVIDER = os.environ.get("BILLING_PROVIDER", "fake")

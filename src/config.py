import os
from pathlib import Path
from dotenv import load_dotenv

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass    

# Ruta raíz del proyecto
ROOT = Path(__file__).resolve().parents[1]

# Cargar variables del .env
load_dotenv(ROOT / ".env")

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")

COUNTRY = "es"
RESULTS_PER_PAGE = 50

DB_PATH = ROOT / "db" / "jobs.sqlite"

KEYWORDS = [
    "data analyst",
    "analista de datos",
    "business intelligence",
    "power bi",
    "sql",
]

def require_env():
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        raise RuntimeError("Faltan ADZUNA_APP_ID / ADZUNA_APP_KEY en .env")
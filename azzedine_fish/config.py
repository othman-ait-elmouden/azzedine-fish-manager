from pathlib import Path
import os

APP_NAME = "Azzedine Fish"
APP_VERSION = "1.0.0"
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = Path(os.getenv("LOCALAPPDATA", BASE_DIR)) / "AzzedineFish"
DB_PATH = DATA_DIR / "azzedine_fish.db"
ASSETS_DIR = BASE_DIR / "assets"
EXPORT_DIR = DATA_DIR / "exports"
BACKUP_DIR = DATA_DIR / "backups"
PRODUCT_IMAGES_DIR = DATA_DIR / "product_images"

PRIMARY = "#0B3954"
ACCENT = "#00A6A6"
ACCENT_HOVER = "#008B8B"
BG_DARK = "#071E2B"
CARD_DARK = "#102F40"
TEXT = "#F3FAFC"
MUTED = "#9DB6C3"
DANGER = "#D9534F"
SUCCESS = "#2BB673"

for path in (DATA_DIR, EXPORT_DIR, BACKUP_DIR, PRODUCT_IMAGES_DIR):
    path.mkdir(parents=True, exist_ok=True)


import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent

load_dotenv(BASE_DIR / ".env")

# ===========================
# Main Bot Configuration
# ===========================

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# ===========================
# PostgreSQL
# ===========================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "ncengine")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASS = os.getenv("DB_PASS", "")

DATABASE_URL = (
    f"postgresql://{DB_USER}:{DB_PASS}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

# ===========================
# Branding
# ===========================

BOT_USERNAME = "@ncenginehost_bot"
SUPPORT_USERNAME = "@ncenginehost_bot"
CHANNEL_USERNAME = "@proxydominates"

POWERED_BY = "Powered By @proxydominates"
HOSTED_TEXT = "Hosted Via @ncenginehost_bot"

# ===========================
# Hosting Limits
# ===========================

MAX_BOTS_PER_USER = 10
MAX_NAME_LENGTH = 30

# ===========================
# Process Settings
# ===========================

HOSTED_FOLDER = BASE_DIR / "hosted_bots"
LOGS_FOLDER = BASE_DIR / "logs"
BACKUP_FOLDER = BASE_DIR / "backups"

HOSTED_FOLDER.mkdir(exist_ok=True)
LOGS_FOLDER.mkdir(exist_ok=True)
BACKUP_FOLDER.mkdir(exist_ok=True)

# ===========================
# Menu Text
# ===========================

START_TEXT = """
🚀 Welcome to NC Engine Host

Host your Telegram bots in just a few clicks.

• Upload 10 Bot Tokens
• Set Your Owner ID
• Set Your Display Name
• Manage Your Hosted Bots

👇 Use the buttons below to continue.
"""

ABOUT_TEXT = f"""
⚡ NC ENGINE HOST

Professional Telegram Bot Hosting.

{POWERED_BY}
"""

# ===========================
# Logging
# ===========================

LOG_LEVEL = "INFO"

import os
from dotenv import load_dotenv

# .env faylni yuklash
load_dotenv()

# Environment variablelarni o'qish
TOKEN = os.getenv("TOKEN")
ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
RESUME_ADMIN_GROUP_ID = int(os.getenv("RESUME_ADMIN_GROUP_ID"))
VACANCY_ADMIN_GROUP_ID = int(os.getenv("VACANCY_ADMIN_GROUP_ID"))
MAIN_CHANNEL_USERNAME = os.getenv("MAIN_CHANNEL_USERNAME")
QUESTION_ADMIN_GROUP_ID = int(os.getenv("QUESTION_ADMIN_GROUP_ID", "0"))
DATABASE_PATH = os.getenv("DATABASE_PATH", "database/bot.db")
RESUME_FOLDER = os.getenv("RESUME_FOLDER", "files/resumes/")
MAX_FILE_SIZE = int(os.getenv("MAX_FILE_SIZE", "10485760"))
ALLOWED_FILE_FORMATS = [x.strip() for x in os.getenv("ALLOWED_FILE_FORMATS", ".pdf,.doc,.docx,.txt").split(",")]
FILE_CLEANUP_HOURS = int(os.getenv("FILE_CLEANUP_HOURS", "24"))  # Fayllar necha soatdan keyin o'chilsin
CLEANUP_INTERVAL_HOURS = int(os.getenv("CLEANUP_INTERVAL_HOURS", "6"))  # Necha soatda bir cleanup ishlaydi
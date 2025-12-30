"""Bot and Dispatcher setup"""
import logging
import os
from aiogram import Bot, Dispatcher
from config import TOKEN, RESUME_FOLDER
from database.migrations import init_db

logger = logging.getLogger(__name__)


def create_bot() -> Bot:
    """Create bot instance"""
    return Bot(token=TOKEN)


def create_dispatcher() -> Dispatcher:
    """Create dispatcher instance"""
    return Dispatcher()


async def setup_bot():
    """Setup bot - create directories and initialize database"""
    logger.info("Bot setup boshlandi...")
    
    os.makedirs("logs", exist_ok=True)
    os.makedirs("database", exist_ok=True)
    os.makedirs(RESUME_FOLDER, exist_ok=True)
    
    logger.info("Database initsializatsiya qilinmoqda...")
    init_db()
    logger.info("Database muvaffaqiyatli initsializatsiya qilindi!")
    
    logger.info("Bot setup yakunlandi!")


async def shutdown_bot(bot: Bot):
    """Shutdown bot"""
    logger.info("Bot to'xtatilmoqda...")
    if hasattr(bot, 'session') and bot.session:
        await bot.session.close()
    logger.info("Bot to'xtatildi!")


"""Main entry point"""
import asyncio
import logging
from logging.handlers import RotatingFileHandler

from app.bot import create_bot, create_dispatcher, setup_bot, shutdown_bot
from app.tasks import start_background_tasks
from config import FILE_CLEANUP_HOURS, CLEANUP_INTERVAL_HOURS
from handlers.start import router as start_router
from handlers.admin import router as admin_router
from handlers.employer import router as employer_router
from handlers.graduate import router as graduate_router
from handlers.student import router as student_router

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        RotatingFileHandler('logs/bot.log', maxBytes=20*1024*1024, backupCount=5, encoding='utf-8'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main function"""
    bot = None
    try:
        # Setup bot
        await setup_bot()
        
        # Start background tasks (file cleanup)
        start_background_tasks(
            cleanup_hours=FILE_CLEANUP_HOURS,
            interval_hours=CLEANUP_INTERVAL_HOURS
        )
        
        # Create bot and dispatcher
        bot = create_bot()
        dp = create_dispatcher()
        
        # Register routers
        logger.info("Handlerlar ro'yxatdan o'tkazilmoqda...")
        dp.include_router(start_router)
        dp.include_router(admin_router)
        dp.include_router(employer_router)
        dp.include_router(graduate_router)
        dp.include_router(student_router)
        
        logger.info("Polling boshlanmoqda...")
        await dp.start_polling(bot, close_bot_session=False)
        
    except Exception as e:
        logger.error(f"Xatolik yuz berdi: {str(e)}", exc_info=True)
    finally:
        if bot:
            await shutdown_bot(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot foydalanuvchi tomonidan to'xtatildi")
    except Exception as e:
        logger.error(f"Kutilmagan xatolik: {str(e)}", exc_info=True)

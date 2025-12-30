"""Background tasks for the bot"""
import asyncio
import logging
from services.file_cleanup_service import FileCleanupService

logger = logging.getLogger(__name__)


async def periodic_file_cleanup(cleanup_hours: int = 24, interval_hours: int = 6):
    """
    Periodic file cleanup task
    
    Args:
        cleanup_hours: Hours after which files should be deleted
        interval_hours: How often to run cleanup (default: every 6 hours)
    """
    cleanup_service = FileCleanupService(cleanup_hours=cleanup_hours)
    
    while True:
        try:
            logger.info("Starting periodic file cleanup...")
            result = cleanup_service.cleanup_old_files()
            
            logger.info(
                f"Cleanup completed: {result['deleted_count']} files deleted, "
                f"{result['total_size_freed'] / 1024 / 1024:.2f} MB freed"
            )
            
            if result['errors']:
                logger.warning(f"Cleanup errors: {result['errors']}")
            
            # Also cleanup orphaned files
            orphaned_result = cleanup_service.cleanup_orphaned_files()
            logger.info(
                f"Orphaned cleanup: {orphaned_result['deleted_count']} files deleted"
            )
            
        except Exception as e:
            logger.error(f"Error in periodic cleanup: {str(e)}", exc_info=True)
        
        # Wait for next interval
        await asyncio.sleep(interval_hours * 3600)


def start_background_tasks(cleanup_hours: int = 24, interval_hours: int = 6):
    """Start background tasks"""
    asyncio.create_task(periodic_file_cleanup(cleanup_hours=cleanup_hours, interval_hours=interval_hours))


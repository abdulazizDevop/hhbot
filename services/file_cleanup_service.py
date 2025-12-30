"""File cleanup service for removing old files"""
import os
import logging
from datetime import datetime, timedelta
from pathlib import Path
from config import RESUME_FOLDER
from database.connection import get_db_connection

logger = logging.getLogger(__name__)


class FileCleanupService:
    """Service for cleaning up old files"""
    
    def __init__(self, cleanup_hours: int = 24):
        """
        Initialize cleanup service
        
        Args:
            cleanup_hours: Hours after which files should be deleted (default: 24)
        """
        self.cleanup_hours = cleanup_hours
    
    def cleanup_old_files(self) -> dict:
        """
        Clean up old files from resume folder
        
        Returns:
            dict with cleanup statistics
        """
        deleted_count = 0
        total_size_freed = 0
        errors = []
        
        try:
            resume_path = Path(RESUME_FOLDER)
            if not resume_path.exists():
                logger.warning(f"Resume folder does not exist: {RESUME_FOLDER}")
                return {
                    'deleted_count': 0,
                    'total_size_freed': 0,
                    'errors': []
                }
            
            cutoff_time = datetime.now() - timedelta(hours=self.cleanup_hours)
            
            # Get all files in resume folder
            for file_path in resume_path.iterdir():
                if file_path.is_file():
                    try:
                        # Check file modification time
                        file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                        
                        if file_mtime < cutoff_time:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            total_size_freed += file_size
                            logger.info(f"Deleted old file: {file_path.name} (age: {datetime.now() - file_mtime})")
                    except Exception as e:
                        error_msg = f"Error deleting {file_path.name}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
            
            logger.info(
                f"Cleanup completed: {deleted_count} files deleted, "
                f"{total_size_freed / 1024 / 1024:.2f} MB freed"
            )
            
        except Exception as e:
            error_msg = f"Error during cleanup: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        return {
            'deleted_count': deleted_count,
            'total_size_freed': total_size_freed,
            'errors': errors
        }
    
    def cleanup_orphaned_files(self) -> dict:
        """
        Clean up files that are not referenced in database
        
        Returns:
            dict with cleanup statistics
        """
        deleted_count = 0
        total_size_freed = 0
        errors = []
        
        try:
            resume_path = Path(RESUME_FOLDER)
            if not resume_path.exists():
                return {
                    'deleted_count': 0,
                    'total_size_freed': 0,
                    'errors': []
                }
            
            # Get all file paths from database
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT file_path FROM ads WHERE status != 'deleted' AND file_path IS NOT NULL")
                rows = cursor.fetchall()
            
            referenced_files = set()
            for row in rows:
                if row[0]:  # file_path
                    file_name = os.path.basename(row[0])
                    referenced_files.add(file_name)
            
            # Check all files in folder
            for file_path in resume_path.iterdir():
                if file_path.is_file():
                    file_name = file_path.name
                    if file_name not in referenced_files:
                        try:
                            file_size = file_path.stat().st_size
                            file_path.unlink()
                            deleted_count += 1
                            total_size_freed += file_size
                            logger.info(f"Deleted orphaned file: {file_name}")
                        except Exception as e:
                            error_msg = f"Error deleting orphaned file {file_name}: {str(e)}"
                            errors.append(error_msg)
                            logger.error(error_msg)
            
            logger.info(
                f"Orphaned files cleanup: {deleted_count} files deleted, "
                f"{total_size_freed / 1024 / 1024:.2f} MB freed"
            )
            
        except Exception as e:
            error_msg = f"Error during orphaned files cleanup: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        return {
            'deleted_count': deleted_count,
            'total_size_freed': total_size_freed,
            'errors': errors
        }


"""Student message repository for database operations"""
from datetime import datetime
from typing import Optional, Tuple, List
from repositories.base import BaseRepository
from database.connection import get_db_connection


class StudentRepository(BaseRepository):
    """Repository for student message database operations"""
    
    def create(
        self,
        user_id: int,
        message_id: int,
        group_message_id: int,
        name: str,
        direction: str,
        group_number: str,
        message_type: str,
        message_text: str
    ) -> int:
        """Create a new student message"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO student_messages 
                (user_id, message_id, group_message_id, name, direction, group_number, 
                 message_type, message_text, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, message_id, group_message_id, name, direction,
                group_number, message_type, message_text, 
                datetime.utcnow().isoformat()
            ))
            return cursor.lastrowid
    
    def get_by_group_message_id(self, group_message_id: int) -> Optional[Tuple]:
        """Get student message by group message ID"""
        return self._execute_query(
            '''SELECT user_id, name, group_number FROM student_messages 
               WHERE group_message_id = ?''',
            (group_message_id,),
            fetch_one=True
        )
    
    def get_by_user_id(self, user_id: int) -> List[Tuple]:
        """Get all messages by user ID"""
        return self._execute_query(
            '''SELECT * FROM student_messages WHERE user_id = ? 
               ORDER BY created_at DESC''',
            (user_id,),
            fetch_all=True
        )


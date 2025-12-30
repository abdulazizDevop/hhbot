"""User repository for database operations"""
from datetime import datetime
from typing import Optional, Tuple
from repositories.base import BaseRepository
from database.connection import get_db_connection


class UserRepository(BaseRepository):
    """Repository for user database operations"""
    
    def create_or_update(
        self, 
        user_id: int, 
        username: str, 
        role: Optional[str] = None, 
        language: Optional[str] = None
    ) -> None:
        """Create or update user"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
            exists = cursor.fetchone()
            
            if exists:
                cursor.execute('''
                    UPDATE users SET username = ?, role = COALESCE(?, role), 
                    language = COALESCE(?, language) WHERE user_id = ?
                ''', (username, role, language, user_id))
            else:
                cursor.execute('''
                    INSERT INTO users (user_id, username, role, language, created_at)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, username, role, language or 'uz', datetime.utcnow().isoformat()))
    
    def get_by_id(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        return self._execute_query(
            'SELECT * FROM users WHERE user_id = ?',
            (user_id,),
            fetch_one=True
        )
    
    def get_stats(self) -> dict:
        """Get user statistics"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM users')
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'graduate'")
            graduates = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'employer'")
            employers = cursor.fetchone()[0]
            
            return {
                'total': total,
                'graduates': graduates,
                'employers': employers
            }


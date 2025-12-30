"""Category repository for database operations"""
from datetime import datetime
from typing import List, Tuple, Optional
from repositories.base import BaseRepository
from database.connection import get_db_connection


class CategoryRepository(BaseRepository):
    """Repository for category database operations"""
    
    def get_all(self) -> List[Tuple[int, str]]:
        """Get all categories"""
        return self._execute_query(
            'SELECT id, name FROM categories ORDER BY name',
            fetch_all=True
        )
    
    def create(self, name: str) -> None:
        """Create a new category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO categories (name, created_at) VALUES (?, ?)
            ''', (name, datetime.utcnow().isoformat()))
    
    def get_by_id(self, category_id: int) -> Optional[Tuple]:
        """Get category by ID"""
        return self._execute_query(
            'SELECT * FROM categories WHERE id = ?',
            (category_id,),
            fetch_one=True
        )
    
    def update_name(self, category_id: int, new_name: str) -> bool:
        """Update category name"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(
                'UPDATE categories SET name = ? WHERE id = ?',
                (new_name, category_id)
            )
            return cursor.rowcount > 0
    
    def delete(self, category_id: int) -> bool:
        """Delete category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM categories WHERE id = ?', (category_id,))
            return cursor.rowcount > 0


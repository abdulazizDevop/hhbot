"""Base repository class"""
from abc import ABC
from typing import Any, Optional
from database.connection import get_db_connection
from config import DATABASE_PATH


class BaseRepository(ABC):
    """Base repository class with common database operations"""
    
    def __init__(self):
        self.db_path = DATABASE_PATH
    
    def _execute_query(
        self, 
        query: str, 
        params: tuple = (), 
        fetch_one: bool = False,
        fetch_all: bool = False
    ) -> Optional[Any]:
        """Execute a query and return results"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if fetch_one:
                return cursor.fetchone()
            elif fetch_all:
                return cursor.fetchall()
            else:
                return cursor.lastrowid
    
    def _execute_many(self, query: str, params_list: list[tuple]) -> None:
        """Execute a query with multiple parameters"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany(query, params_list)


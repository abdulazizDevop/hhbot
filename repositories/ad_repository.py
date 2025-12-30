"""Ad repository for database operations"""
import json
from datetime import datetime
from typing import Optional, List, Tuple, Dict
from repositories.base import BaseRepository
from database.connection import get_db_connection


class AdRepository(BaseRepository):
    """Repository for ad database operations"""
    
    def create(
        self,
        user_id: int,
        ad_type: str,
        data: dict,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None,
        status: str = "draft"
    ) -> int:
        """Create a new ad"""
        now = datetime.utcnow().isoformat()
        
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO ads (user_id, ad_type, status, data, file_id, file_path, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, ad_type, status, 
                json.dumps(data, ensure_ascii=False), 
                file_id, file_path, now, now
            ))
            
            ad_id = cursor.lastrowid
            
            # Add to history
            cursor.execute('''
                INSERT INTO ad_history (ad_id, action, new_data, changed_by, created_at)
                VALUES (?, 'created', ?, ?, ?)
            ''', (ad_id, json.dumps(data, ensure_ascii=False), user_id, now))
            
            return ad_id
    
    def get_by_id(self, ad_id: int) -> Optional[Tuple]:
        """Get ad by ID"""
        return self._execute_query(
            'SELECT * FROM ads WHERE id = ?',
            (ad_id,),
            fetch_one=True
        )
    
    def get_by_user_id(self, user_id: int) -> List[Tuple]:
        """Get all ads by user ID (excluding deleted)"""
        return self._execute_query(
            '''SELECT * FROM ads WHERE user_id = ? AND status != 'deleted'
               ORDER BY created_at DESC''',
            (user_id,),
            fetch_all=True
        )
    
    def get_pending(self, ad_type: Optional[str] = None) -> List[Tuple]:
        """Get pending ads"""
        if ad_type:
            return self._execute_query(
                '''SELECT * FROM ads WHERE status = 'pending' AND ad_type = ?
                   ORDER BY created_at ASC''',
                (ad_type,),
                fetch_all=True
            )
        else:
            return self._execute_query(
                '''SELECT * FROM ads WHERE status = 'pending'
                   ORDER BY created_at ASC''',
                fetch_all=True
            )
    
    def update_status(
        self, 
        ad_id: int, 
        status: str, 
        approved_by: Optional[int] = None
    ) -> bool:
        """Update ad status"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get old status
            cursor.execute('SELECT status FROM ads WHERE id = ?', (ad_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_status = result[0]
            now = datetime.utcnow().isoformat()
            
            # Update status
            if status == 'approved' and approved_by:
                cursor.execute('''
                    UPDATE ads SET status = ?, updated_at = ?, approved_at = ?, approved_by = ?
                    WHERE id = ?
                ''', (status, now, now, approved_by, ad_id))
            else:
                cursor.execute('''
                    UPDATE ads SET status = ?, updated_at = ? WHERE id = ?
                ''', (status, now, ad_id))
            
            # Add to history
            cursor.execute('''
                INSERT INTO ad_history (ad_id, action, old_value, new_value, changed_by, created_at)
                VALUES (?, 'status_changed', ?, ?, ?, ?)
            ''', (ad_id, old_status, status, approved_by or 0, now))
            
            return True
    
    def update_data(
        self,
        ad_id: int,
        new_data: dict,
        new_file_id: Optional[str] = None,
        new_file_path: Optional[str] = None
    ) -> bool:
        """Update ad data"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get old data
            cursor.execute('SELECT data, file_id FROM ads WHERE id = ?', (ad_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            old_data_json, old_file_id = result
            now = datetime.utcnow().isoformat()
            
            # Update data
            if new_file_id and new_file_path:
                cursor.execute('''
                    UPDATE ads SET data = ?, file_id = ?, file_path = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    json.dumps(new_data, ensure_ascii=False), 
                    new_file_id, new_file_path, now, ad_id
                ))
            elif new_file_id:
                cursor.execute('''
                    UPDATE ads SET data = ?, file_id = ?, updated_at = ?
                    WHERE id = ?
                ''', (
                    json.dumps(new_data, ensure_ascii=False), 
                    new_file_id, now, ad_id
                ))
            else:
                cursor.execute('''
                    UPDATE ads SET data = ?, updated_at = ?
                    WHERE id = ?
                ''', (json.dumps(new_data, ensure_ascii=False), now, ad_id))
            
            # Add to history
            cursor.execute('''
                INSERT INTO ad_history (ad_id, action, old_data, new_data, changed_by, created_at)
                VALUES (?, 'updated', ?, ?, ?, ?)
            ''', (
                ad_id, old_data_json, 
                json.dumps(new_data, ensure_ascii=False), 
                0, now
            ))
            
            return True
    
    def update_field(
        self,
        ad_id: int,
        field_name: str,
        old_value: str,
        new_value: str,
        changed_by: int
    ) -> bool:
        """Update a single field in ad"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            # Get current data
            cursor.execute('SELECT data FROM ads WHERE id = ?', (ad_id,))
            result = cursor.fetchone()
            if not result:
                return False
            
            ad_data = json.loads(result[0])
            ad_data[field_name] = new_value
            now = datetime.utcnow().isoformat()
            
            # Update data
            cursor.execute('''
                UPDATE ads SET data = ?, updated_at = ? WHERE id = ?
            ''', (json.dumps(ad_data, ensure_ascii=False), now, ad_id))
            
            # Add to history
            cursor.execute('''
                INSERT INTO ad_history (ad_id, action, field_name, old_value, new_value, changed_by, created_at)
                VALUES (?, 'field_updated', ?, ?, ?, ?, ?)
            ''', (ad_id, field_name, old_value, new_value, changed_by, now))
            
            return True
    
    def get_approved_by_category(self, category_name: str, limit: int = 20) -> List[Tuple]:
        """Get approved ads by category"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM ads WHERE status = 'approved' 
                ORDER BY approved_at DESC NULLS LAST, created_at DESC
            """)
            rows = cursor.fetchall()
        
        results = []
        for row in rows:
            try:
                data = json.loads(row[4])
            except Exception:
                continue
            
            if row[2] == 'employer' and data.get('category') == category_name:
                results.append(row)
            elif row[2] == 'graduate' and data.get('profession') == category_name:
                results.append(row)
            
            if len(results) >= limit:
                break
        
        return results
    
    def get_stats(self) -> Dict[str, int]:
        """Get ad statistics"""
        with get_db_connection() as conn:
            cursor = conn.cursor()
            
            cursor.execute('SELECT COUNT(*) FROM ads')
            total = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'approved'")
            approved = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'pending'")
            pending = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'rejected'")
            rejected = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM ads WHERE status = 'cancelled'")
            cancelled = cursor.fetchone()[0]
            
            return {
                'total': total,
                'approved': approved,
                'pending': pending,
                'rejected': rejected,
                'cancelled': cancelled
            }
    
    def get_history(self, ad_id: int) -> List[Tuple]:
        """Get ad history"""
        return self._execute_query(
            '''SELECT * FROM ad_history WHERE ad_id = ? 
               ORDER BY created_at DESC''',
            (ad_id,),
            fetch_all=True
        )


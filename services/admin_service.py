"""Admin service for admin panel business logic"""
from typing import Dict, List, Tuple
from services.user_service import UserService
from services.ad_service import AdService
from services.category_service import CategoryService
from utils.text_formatters import format_ad_text, format_date, get_status_text
import json


class AdminService:
    """Service for admin panel business logic"""
    
    def __init__(self):
        self.user_service = UserService()
        self.ad_service = AdService()
        self.category_service = CategoryService()
    
    def get_full_statistics(self) -> Dict:
        """Get full statistics for admin panel"""
        user_stats = self.user_service.get_user_stats()
        ad_stats = self.ad_service.get_ad_stats()
        
        return {
            'users': user_stats,
            'ads': ad_stats
        }
    
    def format_pending_ad_details(self, ad: Tuple, language: str = "uz") -> str:
        """Format pending ad with full details"""
        ad_id, user_id, ad_type, status, data, file_id, file_path, created_at, updated_at, approved_at, approved_by = ad
        
        try:
            ad_data = json.loads(data)
        except Exception:
            ad_data = {}
        
        # Get user info
        user = self.user_service.get_user(user_id)
        username = user[1] if user else "Noma'lum"
        
        # Format ad text
        ad_text = format_ad_text(ad_data, ad_type, language)
        created_date = format_date(created_at)
        status_text = get_status_text(status, language)
        
        # Build full text
        full_text = (
            f"📋 <b>E'lon #{ad_id}</b>\n"
            f"👤 <b>Foydalanuvchi:</b> @{username} (ID: {user_id})\n"
            f"📊 <b>Status:</b> {status_text}\n"
            f"📅 <b>Yaratildi:</b> {created_date}\n"
            f"🏷 <b>Tur:</b> {ad_type}\n\n"
            f"{ad_text}"
        )
        
        if file_id:
            full_text += f"\n📄 <b>Resume:</b> Yuklangan ✅"
        
        return full_text
    
    def get_pending_ads_list(self, limit: int = 20) -> List[Dict]:
        """Get pending ads with formatted details"""
        ads = self.ad_service.get_pending_ads()
        result = []
        
        for ad in ads[:limit]:
            ad_id, user_id, ad_type, status, data, file_id, file_path, created_at, updated_at, approved_at, approved_by = ad
            
            try:
                ad_data = json.loads(data)
            except Exception:
                ad_data = {}
            
            user = self.user_service.get_user(user_id)
            username = user[1] if user else "Noma'lum"
            
            if ad_type == "graduate":
                title = ad_data.get('name', 'Nomsiz')
            else:
                title = ad_data.get('company', ad_data.get('name', 'Nomsiz'))
            
            result.append({
                'ad_id': ad_id,
                'user_id': user_id,
                'username': username,
                'ad_type': ad_type,
                'title': title,
                'status': status,
                'created_at': created_at,
                'has_file': bool(file_id)
            })
        
        return result


"""Ad service for business logic"""
from typing import Optional, Dict, List, Tuple
from repositories.ad_repository import AdRepository
from services.validation_service import ValidationService


class AdService:
    """Service for ad business logic"""
    
    def __init__(self):
        self.repository = AdRepository()
        self.validator = ValidationService()
    
    def create_ad(
        self,
        user_id: int,
        ad_type: str,
        data: dict,
        file_id: Optional[str] = None,
        file_path: Optional[str] = None,
        status: str = "draft"
    ) -> int:
        """Create a new ad"""
        return self.repository.create(user_id, ad_type, data, file_id, file_path, status)
    
    def get_ad(self, ad_id: int) -> Optional[Tuple]:
        """Get ad by ID"""
        return self.repository.get_by_id(ad_id)
    
    def get_user_ads(self, user_id: int) -> List[Tuple]:
        """Get all ads by user ID"""
        return self.repository.get_by_user_id(user_id)
    
    def get_pending_ads(self, ad_type: Optional[str] = None) -> List[Tuple]:
        """Get pending ads"""
        return self.repository.get_pending(ad_type)
    
    def update_ad_status(
        self,
        ad_id: int,
        status: str,
        approved_by: Optional[int] = None
    ) -> bool:
        """Update ad status"""
        return self.repository.update_status(ad_id, status, approved_by)
    
    def update_ad_data(
        self,
        ad_id: int,
        new_data: dict,
        new_file_id: Optional[str] = None,
        new_file_path: Optional[str] = None
    ) -> bool:
        """Update ad data"""
        return self.repository.update_data(ad_id, new_data, new_file_id, new_file_path)
    
    def update_ad_field(
        self,
        ad_id: int,
        field_name: str,
        old_value: str,
        new_value: str,
        changed_by: int
    ) -> bool:
        """Update a single field in ad"""
        return self.repository.update_field(ad_id, field_name, old_value, new_value, changed_by)
    
    def get_approved_ads_by_category(self, category_name: str, limit: int = 20) -> List[Tuple]:
        """Get approved ads by category"""
        return self.repository.get_approved_by_category(category_name, limit)
    
    def get_ad_stats(self) -> Dict[str, int]:
        """Get ad statistics"""
        return self.repository.get_stats()
    
    def get_ad_history(self, ad_id: int) -> List[Tuple]:
        """Get ad history"""
        return self.repository.get_history(ad_id)
    
    def validate_ad_data(self, ad_type: str, data: dict) -> Tuple[bool, Optional[str]]:
        """Validate ad data based on type"""
        if ad_type == "graduate":
            required_fields = ["name", "age", "technologies", "contact", "region", "price", "profession"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return False, f"{field} maydoni to'ldirilishi kerak"
            
            # Validate age
            is_valid, error = self.validator.validate_age(data.get("age", ""))
            if not is_valid:
                return False, error
            
            # Validate phone
            if not self.validator.validate_phone(data.get("contact", "")):
                return False, "Telefon raqam noto'g'ri"
        
        elif ad_type == "employer":
            required_fields = ["company", "name", "age", "category", "location", "salary"]
            for field in required_fields:
                if field not in data or not data[field]:
                    return False, f"{field} maydoni to'ldirilishi kerak"
            
            # Validate age
            is_valid, error = self.validator.validate_age(data.get("age", ""), 18, 65)
            if not is_valid:
                return False, error
            
            # Validate salary
            is_valid, error = self.validator.validate_salary(data.get("salary", ""))
            if not is_valid:
                return False, error
        
        return True, None


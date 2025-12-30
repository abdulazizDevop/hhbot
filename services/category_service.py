"""Category service for business logic"""
from typing import List, Tuple, Optional
from repositories.category_repository import CategoryRepository
from services.validation_service import ValidationService


class CategoryService:
    """Service for category business logic"""
    
    def __init__(self):
        self.repository = CategoryRepository()
        self.validator = ValidationService()
    
    def get_all_categories(self) -> List[Tuple[int, str]]:
        """Get all categories"""
        return self.repository.get_all()
    
    def create_category(self, name: str) -> Tuple[bool, Optional[str]]:
        """Create a new category"""
        # Validate name
        is_valid, error = self.validator.validate_text_length(name, 2, 50)
        if not is_valid:
            return False, error
        
        try:
            self.repository.create(name)
            return True, None
        except Exception as e:
            return False, f"Kategoriya qo'shishda xatolik: {str(e)}"
    
    def get_category_by_id(self, category_id: int) -> Optional[Tuple]:
        """Get category by ID"""
        return self.repository.get_by_id(category_id)
    
    def update_category_name(self, category_id: int, new_name: str) -> Tuple[bool, Optional[str]]:
        """Update category name"""
        # Validate name
        is_valid, error = self.validator.validate_text_length(new_name, 2, 50)
        if not is_valid:
            return False, error
        
        success = self.repository.update_name(category_id, new_name)
        if not success:
            return False, "Kategoriya topilmadi"
        return True, None
    
    def delete_category(self, category_id: int) -> Tuple[bool, Optional[str]]:
        """Delete category"""
        success = self.repository.delete(category_id)
        if not success:
            return False, "Kategoriya topilmadi"
        return True, None


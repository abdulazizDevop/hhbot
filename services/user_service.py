"""User service for business logic"""
from typing import Optional, Tuple
from repositories.user_repository import UserRepository


class UserService:
    """Service for user business logic"""
    
    def __init__(self):
        self.repository = UserRepository()
    
    def create_or_update_user(
        self,
        user_id: int,
        username: Optional[str],
        role: Optional[str] = None,
        language: Optional[str] = None
    ) -> None:
        """Create or update user"""
        self.repository.create_or_update(user_id, username or "None", role, language)
    
    def get_user(self, user_id: int) -> Optional[Tuple]:
        """Get user by ID"""
        return self.repository.get_by_id(user_id)
    
    def get_user_language(self, user_id: int, default: str = "uz") -> str:
        """Get user language"""
        user = self.get_user(user_id)
        if user and user[3]:
            return user[3]
        return default
    
    def check_user_role(self, user_id: int, required_role: str) -> Tuple[bool, str]:
        """Check if user has required role"""
        user = self.get_user(user_id)
        if not user:
            return False, "uz"
        if user[2] != required_role:
            return False, user[3] or "uz"
        return True, user[3] or "uz"
    
    def get_user_stats(self) -> dict:
        """Get user statistics"""
        return self.repository.get_stats()


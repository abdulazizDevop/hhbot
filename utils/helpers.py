"""Helper functions"""
from typing import Tuple
from services.user_service import UserService


def get_user_language(user_id: int, default: str = "uz") -> str:
    """Get user language"""
    user_service = UserService()
    return user_service.get_user_language(user_id, default)


def check_user_role(user_id: int, required_role: str) -> Tuple[bool, str]:
    """Check if user has required role
    
    Returns:
        Tuple[bool, str]: (is_valid, language)
    """
    user_service = UserService()
    return user_service.check_user_role(user_id, required_role)


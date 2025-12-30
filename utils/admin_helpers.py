"""Admin helper functions"""
from config import ADMIN_IDS


def is_admin(user_id: int) -> bool:
    """Check if user is admin - centralized function"""
    return user_id in ADMIN_IDS


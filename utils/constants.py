"""Constants used throughout the application"""
from typing import Dict

# User roles
USER_ROLES = {
    'GRADUATE': 'graduate',
    'EMPLOYER': 'employer',
    'STUDENT': 'student',
}

# Ad types
AD_TYPES = {
    'GRADUATE': 'graduate',
    'EMPLOYER': 'employer',
}

# Ad statuses
AD_STATUSES = {
    'DRAFT': 'draft',
    'PENDING': 'pending',
    'APPROVED': 'approved',
    'REJECTED': 'rejected',
    'CANCELLED': 'cancelled',
    'DELETED': 'deleted',
}

# Status emoji mapping
STATUS_EMOJI: Dict[str, str] = {
    'draft': '📝',
    'pending': '⏳',
    'approved': '✅',
    'rejected': '❌',
    'cancelled': '🚫',
    'deleted': '🗑',
}

# Age limits
MIN_AGE = 16
MAX_AGE = 65
MIN_AGE_EMPLOYER = 18

# Default values
DEFAULT_LANGUAGE = 'uz'

# File limits
MAX_FILE_SIZE = 10485760  # 10MB
ALLOWED_FILE_FORMATS = ['.pdf', '.doc', '.docx', '.txt']

# Text length limits
MIN_TEXT_LENGTH = 2
MAX_TEXT_LENGTH = 50
MIN_CATEGORY_NAME_LENGTH = 2
MAX_CATEGORY_NAME_LENGTH = 50
MIN_STUDENT_MESSAGE_LENGTH = 10


"""Student message service for business logic"""
from typing import Optional, Tuple
from repositories.student_repository import StudentRepository
from services.validation_service import ValidationService


class StudentService:
    """Service for student message business logic"""
    
    def __init__(self):
        self.repository = StudentRepository()
        self.validator = ValidationService()
    
    def create_message(
        self,
        user_id: int,
        message_id: int,
        group_message_id: int,
        name: str,
        direction: str,
        group_number: str,
        message_type: str,
        message_text: str
    ) -> int:
        """Create a new student message"""
        return self.repository.create(
            user_id, message_id, group_message_id, name, direction,
            group_number, message_type, message_text
        )
    
    def get_message_by_group_id(self, group_message_id: int) -> Optional[Tuple]:
        """Get student message by group message ID"""
        return self.repository.get_by_group_message_id(group_message_id)
    
    def validate_student_message(
        self,
        name: str,
        group_number: str,
        message_text: str
    ) -> Tuple[bool, Optional[str]]:
        """Validate student message data"""
        # Validate name
        is_valid, error = self.validator.validate_text_length(name, 2)
        if not is_valid:
            return False, error
        
        # Validate group number
        is_valid, error = self.validator.validate_text_length(group_number, 2)
        if not is_valid:
            return False, error
        
        # Validate message text
        is_valid, error = self.validator.validate_text_length(message_text, 10)
        if not is_valid:
            return False, error
        
        return True, None


"""Validation service for input validation"""
import re
from typing import Tuple, Optional


class ValidationService:
    """Service for validation logic"""
    
    @staticmethod
    def validate_phone(phone: str) -> bool:
        """Validate phone number"""
        pattern = r'^(\+998|998)?[0-9]{9}$'
        cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        return bool(re.match(pattern, cleaned))
    
    @staticmethod
    def clean_phone(phone: str) -> str:
        """Clean phone number"""
        cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
        if cleaned.startswith('998'):
            cleaned = '+' + cleaned
        elif cleaned.startswith('8') and len(cleaned) == 9:
            cleaned = '+998' + cleaned[1:]
        elif not cleaned.startswith('+'):
            cleaned = '+998' + cleaned
        return cleaned
    
    @staticmethod
    def validate_age(age: str, min_age: int = 16, max_age: int = 65) -> Tuple[bool, Optional[str]]:
        """Validate age"""
        if not age.isdigit():
            return False, "Yosh raqam bo'lishi kerak"
        age_int = int(age)
        if age_int < min_age or age_int > max_age:
            return False, f"Yosh {min_age}-{max_age} orasida bo'lishi kerak"
        return True, None
    
    @staticmethod
    def validate_text_length(text: str, min_length: int, max_length: Optional[int] = None) -> Tuple[bool, Optional[str]]:
        """Validate text length"""
        if not text or len(text) < min_length:
            return False, f"Matn kamida {min_length} belgi bo'lishi kerak"
        if max_length and len(text) > max_length:
            return False, f"Matn {max_length} belgidan oshmasligi kerak"
        return True, None
    
    @staticmethod
    def validate_salary(salary: str) -> Tuple[bool, Optional[str]]:
        """Validate salary"""
        cleaned = salary.replace('$', '').replace(' ', '').replace(',', '')
        if not cleaned.isdigit():
            return False, "Maosh raqam bo'lishi kerak"
        return True, None
    
    @staticmethod
    def validate_gender(gender: str) -> Tuple[bool, Optional[str]]:
        """Validate gender"""
        valid_genders = ["erkak", "ayol", "farqi yo'q", "ahamiyatsiz", "мужчина", "женщина", "не важно"]
        if not gender or gender.lower() not in valid_genders:
            return False, "Jins noto'g'ri (erkak, ayol, farqi yo'q)"
        return True, None


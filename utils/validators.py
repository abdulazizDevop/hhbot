"""Validation utilities"""
import re


def validate_phone(phone: str) -> bool:
    """Validate phone number"""
    pattern = r'^(\+998|998)?[0-9]{9}$'
    cleaned = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    return bool(re.match(pattern, cleaned))


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


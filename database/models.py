"""Database models and schema definitions"""
from typing import Optional
from dataclasses import dataclass


@dataclass
class User:
    """User model"""
    user_id: int
    username: Optional[str]
    role: Optional[str]
    language: str
    created_at: str


@dataclass
class Ad:
    """Ad model"""
    id: int
    user_id: int
    ad_type: str
    status: str
    data: dict
    file_id: Optional[str]
    file_path: Optional[str]
    created_at: str
    updated_at: str
    approved_at: Optional[str]
    approved_by: Optional[int]


@dataclass
class Category:
    """Category model"""
    id: int
    name: str
    created_at: str


@dataclass
class StudentMessage:
    """Student message model"""
    id: int
    user_id: int
    message_id: int
    group_message_id: int
    name: str
    direction: str
    group_number: str
    message_type: str
    message_text: str
    created_at: str


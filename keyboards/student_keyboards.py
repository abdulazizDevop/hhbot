"""Student keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from data.languages import get_text
from services.category_service import CategoryService


def student_main_menu(language: str) -> InlineKeyboardMarkup:
    """Student main menu"""
    keyboard = [
        [InlineKeyboardButton(text=get_text("student_send", language), callback_data="student_send")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def student_type_keyboard(language: str) -> InlineKeyboardMarkup:
    """Student type selection keyboard"""
    keyboard = [[
        InlineKeyboardButton(text=get_text("student_type_suggest", language), callback_data="student_type_suggest"),
        InlineKeyboardButton(text=get_text("student_type_complaint", language), callback_data="student_type_complaint")
    ]]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def student_confirmation_keyboard(language: str) -> InlineKeyboardMarkup:
    """Student confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text=get_text("confirm_btn", language), callback_data="confirm_ad"),
            InlineKeyboardButton(text=get_text("cancel_btn", language), callback_data="cancel_ad")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def student_directions_keyboard() -> InlineKeyboardMarkup:
    """Student directions keyboard"""
    category_service = CategoryService()
    categories = category_service.get_all_categories()
    keyboard = []
    
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(text=categories[i][1], callback_data=f"student_dir_{categories[i][0]}")]
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(text=categories[i + 1][1], callback_data=f"student_dir_{categories[i + 1][0]}"))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


"""Employer keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from data.languages import get_text
from services.category_service import CategoryService


def employer_main_menu(language: str) -> ReplyKeyboardMarkup:
    """Employer main menu"""
    keyboard = [
        [
            KeyboardButton(text="👔 " + get_text("create_ad", language)),
            KeyboardButton(text="👔 " + get_text("my_ads", language))
        ],
        [
            KeyboardButton(text=get_text("contact_admin", language))
        ],
        [
            KeyboardButton(text=get_text("browse_by_category", language))
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def edit_fields_keyboard_employer(language: str) -> InlineKeyboardMarkup:
    """Edit fields keyboard for employer"""
    fields = [
        ("edit_name", "name"),
        ("edit_company", "company"),
        ("edit_category", "category"),
        ("edit_age", "age"),
        ("edit_gender", "gender"),
        ("edit_experience", "experience"),
        ("edit_work_days", "work_days"),
        ("edit_work_hours", "work_hours"),
        ("edit_location", "location"),
        ("edit_salary", "salary"),
        ("edit_requirements", "requirements")
    ]
    
    keyboard = []
    for i in range(0, len(fields), 2):
        row = [InlineKeyboardButton(
            text=get_text(fields[i][0], language),
            callback_data=f"edit_field_{fields[i][1]}"
        )]
        if i + 1 < len(fields):
            row.append(InlineKeyboardButton(
                text=get_text(fields[i + 1][0], language),
                callback_data=f"edit_field_{fields[i + 1][1]}"
            ))
        keyboard.append(row)
    
    keyboard.append([InlineKeyboardButton(text=get_text("back", language), callback_data="back_to_confirm")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def browse_categories_keyboard() -> InlineKeyboardMarkup:
    """Browse categories keyboard"""
    category_service = CategoryService()
    categories = category_service.get_all_categories()
    keyboard = []
    
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(text=f"📂 {categories[i][1]}", callback_data=f"browse_cat_{categories[i][0]}")]
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(text=f"📂 {categories[i + 1][1]}", callback_data=f"browse_cat_{categories[i + 1][0]}"))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def ad_actions_keyboard_employer(ad_id: int, status: str, language: str) -> InlineKeyboardMarkup:
    """Ad actions keyboard for employer"""
    keyboard = []
    
    if status == 'draft':
        keyboard.append([
            InlineKeyboardButton(text=get_text("confirm_btn", language), callback_data=f"emp_confirm_draft_{ad_id}"),
            InlineKeyboardButton(text=get_text("edit_btn", language), callback_data=f"emp_edit_draft_{ad_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"emp_delete_{ad_id}")
        ])
    elif status == 'pending':
        keyboard.append([
            InlineKeyboardButton(text=get_text("edit_btn", language), callback_data=f"emp_edit_pending_{ad_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text=get_text("cancel_btn", language), callback_data=f"emp_cancel_pending_{ad_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"emp_delete_{ad_id}")
        ])
    elif status in ['approved', 'rejected', 'cancelled']:
        keyboard.append([
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"emp_delete_{ad_id}"),
            InlineKeyboardButton(text=get_text("back", language), callback_data="my_ads")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


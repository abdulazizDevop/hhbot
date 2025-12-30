"""Base keyboard functions"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from data.languages import LANGUAGES, get_text
from services.category_service import CategoryService


def language_keyboard() -> InlineKeyboardMarkup:
    """Language selection keyboard"""
    keyboard = []
    for code, name in LANGUAGES.items():
        keyboard.append([InlineKeyboardButton(text=name, callback_data=f"lang_{code}")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def role_keyboard(language: str) -> InlineKeyboardMarkup:
    """Role selection keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(
                text=get_text("graduate", language),
                callback_data="role_graduate"
            ),
            InlineKeyboardButton(
                text=get_text("employer", language),
                callback_data="role_employer"
            )
        ],
        [
            InlineKeyboardButton(
                text=get_text("student", language),
                callback_data="role_student"
            )
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def contact_keyboard(language: str) -> ReplyKeyboardMarkup:
    """Contact sharing keyboard"""
    keyboard = [
        [KeyboardButton(text=get_text("share_contact", language), request_contact=True)]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def regions_keyboard(language: str) -> InlineKeyboardMarkup:
    """Regions selection keyboard"""
    regions = get_text("regions", language)
    keyboard = []
    
    for i in range(0, len(regions), 2):
        row = [InlineKeyboardButton(text=regions[i], callback_data=f"region_{i}")]
        if i + 1 < len(regions):
            row.append(InlineKeyboardButton(text=regions[i + 1], callback_data=f"region_{i+1}"))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def categories_keyboard() -> InlineKeyboardMarkup:
    """Categories selection keyboard"""
    category_service = CategoryService()
    categories = category_service.get_all_categories()
    keyboard = []
    
    for i in range(0, len(categories), 2):
        row = [InlineKeyboardButton(text=categories[i][1], callback_data=f"category_{categories[i][0]}")]
        if i + 1 < len(categories):
            row.append(InlineKeyboardButton(text=categories[i + 1][1], callback_data=f"category_{categories[i + 1][0]}"))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def confirmation_keyboard(language: str) -> InlineKeyboardMarkup:
    """Confirmation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text=get_text("confirm_btn", language), callback_data="confirm_ad"),
            InlineKeyboardButton(text=get_text("edit_btn", language), callback_data="edit_ad"),
            InlineKeyboardButton(text=get_text("cancel_btn", language), callback_data="cancel_ad")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def create_inline_keyboard_from_list(
    items: list,
    callback_prefix: str,
    items_per_row: int = 2,
    get_text_func=None
) -> InlineKeyboardMarkup:
    """Create inline keyboard from a list of items"""
    keyboard = []
    
    for i in range(0, len(items), items_per_row):
        row = []
        for j in range(items_per_row):
            if i + j < len(items):
                item = items[i + j]
                if isinstance(item, tuple):
                    item_id, item_text = item
                    text = get_text_func(item_text) if get_text_func else item_text
                    row.append(InlineKeyboardButton(
                        text=text,
                        callback_data=f"{callback_prefix}_{item_id}"
                    ))
                else:
                    row.append(InlineKeyboardButton(
                        text=str(item),
                        callback_data=f"{callback_prefix}_{i + j}"
                    ))
        keyboard.append(row)
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


"""Graduate keyboards"""
import json
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from data.languages import get_text
from utils.constants import STATUS_EMOJI


def graduate_main_menu(language: str) -> ReplyKeyboardMarkup:
    """Graduate main menu"""
    keyboard = [
        [
            KeyboardButton(text="🎓 " + get_text("create_ad", language)),
            KeyboardButton(text="🎓 " + get_text("my_ads", language))
        ]
    ]
    return ReplyKeyboardMarkup(keyboard=keyboard, resize_keyboard=True, one_time_keyboard=True)


def edit_fields_keyboard_graduate(language: str) -> InlineKeyboardMarkup:
    """Edit fields keyboard for graduate"""
    fields = [
        ("edit_name", "name"),
        ("edit_age", "age"),
        ("edit_technologies", "technologies"),
        ("edit_contact", "contact"),
        ("edit_region", "region"),
        ("edit_price", "price"),
        ("edit_profession", "profession"),
        ("edit_contact_time", "contact_time"),
        ("edit_goal", "goal")
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


def my_ads_keyboard(ads, language: str) -> InlineKeyboardMarkup:
    """My ads keyboard"""
    keyboard = []
    
    for ad in ads:
        ad_id, user_id, ad_type, status, data, file_id, file_path, created_at, updated_at, approved_at, approved_by = ad
        
        status_emoji = STATUS_EMOJI.get(status, '❓')
        
        try:
            ad_data = json.loads(data)
            if ad_type == "graduate":
                title = ad_data.get('name', 'Nomsiz')[:30]
            else:
                title = ad_data.get('company', ad_data.get('name', 'Nomsiz'))[:30]
        except Exception:
            title = 'Noma\'lum'
        
        button_text = f"{status_emoji} {title}..."
        
        if ad_type == "graduate":
            callback_data = f"grad_view_{ad_id}"
        else:
            callback_data = f"emp_view_{ad_id}"
        
        keyboard.append([InlineKeyboardButton(
            text=button_text,
            callback_data=callback_data
        )])
    
    keyboard.append([InlineKeyboardButton(text=get_text("main_menu", language), callback_data="main_menu")])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def ad_actions_keyboard_graduate(ad_id: int, status: str, language: str) -> InlineKeyboardMarkup:
    """Ad actions keyboard for graduate"""
    keyboard = []
    
    if status == 'draft':
        keyboard.append([
            InlineKeyboardButton(text=get_text("confirm_btn", language), callback_data=f"grad_confirm_draft_{ad_id}"),
            InlineKeyboardButton(text=get_text("edit_btn", language), callback_data=f"grad_edit_draft_{ad_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"grad_delete_{ad_id}")
        ])
    elif status == 'pending':
        keyboard.append([
            InlineKeyboardButton(text=get_text("edit_btn", language), callback_data=f"grad_edit_pending_{ad_id}")
        ])
        keyboard.append([
            InlineKeyboardButton(text=get_text("cancel_btn", language), callback_data=f"grad_cancel_pending_{ad_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"grad_delete_{ad_id}")
        ])
    elif status in ['approved', 'rejected', 'cancelled']:
        keyboard.append([
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"grad_delete_{ad_id}"),
            InlineKeyboardButton(text=get_text("back", language), callback_data="my_ads")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


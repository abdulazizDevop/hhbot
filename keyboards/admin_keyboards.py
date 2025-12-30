"""Admin keyboards"""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from services.category_service import CategoryService


def admin_panel_keyboard() -> InlineKeyboardMarkup:
    """Admin panel keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📊 Statistika", callback_data="stats"),
            InlineKeyboardButton(text="⏳ Kutilayotgan e'lonlar", callback_data="pending_ads")
        ],
        [
            InlineKeyboardButton(text="📂 Kategoriyalar", callback_data="manage_categories")
        ],
        [
            InlineKeyboardButton(text="🚪 Chiqish", callback_data="exit_admin")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_moderation_keyboard(ad_id: int) -> InlineKeyboardMarkup:
    """Admin moderation keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{ad_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{ad_id}")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def admin_categories_keyboard() -> InlineKeyboardMarkup:
    """Admin categories management keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="📂 Kategoriyalar ro'yxati", callback_data="list_categories"),
            InlineKeyboardButton(text="➕ Kategoriya qo'shish", callback_data="add_category")
        ],
        [
            InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def categories_list_keyboard() -> InlineKeyboardMarkup:
    """Categories list keyboard"""
    category_service = CategoryService()
    categories = category_service.get_all_categories()
    keyboard = []
    
    for cat_id, cat_name in categories:
        keyboard.append([
            InlineKeyboardButton(
                text=f"📂 {cat_name}",
                callback_data=f"edit_category_{cat_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="➕ Yangi qo'shish", callback_data="add_category"),
        InlineKeyboardButton(text="🏠 Orqaga", callback_data="manage_categories")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def category_actions_keyboard(cat_id: int) -> InlineKeyboardMarkup:
    """Category actions keyboard"""
    keyboard = [
        [
            InlineKeyboardButton(text="✏️ Tahrirlash", callback_data=f"edit_cat_name_{cat_id}"),
            InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"delete_cat_{cat_id}")
        ],
        [
            InlineKeyboardButton(text="🏠 Orqaga", callback_data="list_categories")
        ]
    ]
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


def pending_ads_list_keyboard(ads_list: list) -> InlineKeyboardMarkup:
    """Pending ads list keyboard"""
    keyboard = []
    
    for ad_info in ads_list:
        ad_id = ad_info['ad_id']
        title = ad_info['title'][:30]
        ad_type_emoji = "🎓" if ad_info['ad_type'] == "graduate" else "👔"
        file_emoji = "📄" if ad_info['has_file'] else ""
        
        button_text = f"{ad_type_emoji} #{ad_id} - {title}... {file_emoji}"
        keyboard.append([
            InlineKeyboardButton(
                text=button_text,
                callback_data=f"view_pending_ad_{ad_id}"
            )
        ])
    
    keyboard.append([
        InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=keyboard)


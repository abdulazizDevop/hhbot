"""Keyboard modules"""
from keyboards.base import (
    language_keyboard,
    role_keyboard,
    contact_keyboard,
    regions_keyboard,
    categories_keyboard,
    confirmation_keyboard,
    create_inline_keyboard_from_list
)
from keyboards.admin_keyboards import (
    admin_panel_keyboard,
    admin_moderation_keyboard,
    admin_categories_keyboard,
    categories_list_keyboard,
    category_actions_keyboard,
    pending_ads_list_keyboard
)
from keyboards.graduate_keyboards import (
    graduate_main_menu,
    edit_fields_keyboard_graduate,
    my_ads_keyboard,
    ad_actions_keyboard_graduate
)
from keyboards.employer_keyboards import (
    employer_main_menu,
    edit_fields_keyboard_employer,
    browse_categories_keyboard
)
from keyboards.student_keyboards import (
    student_main_menu,
    student_type_keyboard,
    student_confirmation_keyboard,
    student_directions_keyboard
)

__all__ = [
    'language_keyboard',
    'role_keyboard',
    'contact_keyboard',
    'regions_keyboard',
    'categories_keyboard',
    'confirmation_keyboard',
    'create_inline_keyboard_from_list',
    'admin_panel_keyboard',
    'admin_moderation_keyboard',
    'admin_categories_keyboard',
    'categories_list_keyboard',
    'category_actions_keyboard',
    'pending_ads_list_keyboard',
    'graduate_main_menu',
    'edit_fields_keyboard_graduate',
    'my_ads_keyboard',
    'ad_actions_keyboard_graduate',
    'employer_main_menu',
    'edit_fields_keyboard_employer',
    'browse_categories_keyboard',
    'student_main_menu',
    'student_type_keyboard',
    'student_confirmation_keyboard',
    'student_directions_keyboard',
]


# handlers/start.py
from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext

from data.languages import get_text
from keyboards.base import language_keyboard, role_keyboard
from keyboards.graduate_keyboards import graduate_main_menu
from keyboards.employer_keyboards import employer_main_menu
from keyboards.student_keyboards import student_main_menu
from services.user_service import UserService
from config import ADMIN_IDS

router = Router()

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    """Start komandasi"""
    await state.clear()
    user_id = message.from_user.id
    username = message.from_user.username
    
    # Foydalanuvchini bazaga qo'shish
    user_service = UserService()
    user_service.create_or_update_user(user_id, username)
    
    await message.answer(
        get_text("welcome", "uz"),
        reply_markup=language_keyboard()
    )

@router.callback_query(F.data.startswith("lang_"))
async def select_language(callback: CallbackQuery, state: FSMContext):
    """Til tanlash"""
    language = callback.data.split("_")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    # Tilni saqlash
    user_service = UserService()
    user_service.create_or_update_user(user_id, username, language=language)
    await state.update_data(language=language)
    
    await callback.message.edit_text(
        get_text("select_role", language),
        reply_markup=role_keyboard(language)
    )

@router.callback_query(F.data.startswith("role_"))
async def select_role(callback: CallbackQuery, state: FSMContext):
    """Rol tanlash"""
    role = callback.data.split("_")[1]
    user_id = callback.from_user.id
    username = callback.from_user.username
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    # Rolni saqlash
    user_service = UserService()
    user_service.create_or_update_user(user_id, username, role=role, language=language)
    await state.update_data(role=role)
    
    if role == "graduate":
        await callback.message.answer(
            f"🎓 {get_text('graduate', language)} sifatida xush kelibsiz!",
            reply_markup=graduate_main_menu(language)
        )
    elif role == "student":
        # Reply keyboardni olib tashlash (bo'sh bo'lmagan matn bilan)
        await callback.message.answer(".", reply_markup=ReplyKeyboardRemove())
        await callback.message.answer(
            f"📚 {get_text('student', language)} sifatida xush kelibsiz!",
            reply_markup=student_main_menu(language)
        )
    else:  # employer
        await callback.message.answer(
            f"👔 {get_text('employer', language)} sifatida xush kelibsiz!",
            reply_markup=employer_main_menu(language)
        )
    
    await callback.message.delete()

@router.callback_query(F.data == "main_menu")
async def main_menu(callback: CallbackQuery, state: FSMContext):
    """Asosiy menyuga qaytish"""
    user_service = UserService()
    user = user_service.get_user(callback.from_user.id)
    if not user:
        await callback.answer("Iltimos /start ni bosing")
        return
    
    user_id, username, role, language, created_at = user
    await state.update_data(language=language, role=role)
    
    if role == "graduate":
        await callback.message.answer(
            f"🎓 {get_text('graduate', language)} asosiy menyu",
            reply_markup=graduate_main_menu(language)
        )
    else:  # employer
        await callback.message.answer(
            f"👔 {get_text('employer', language)} asosiy menyu",
            reply_markup=employer_main_menu(language)
        )
    
    await callback.message.delete()

@router.message(Command("admin"))
async def cmd_admin(message: Message):
    """Admin panel"""
    if message.from_user.id not in ADMIN_IDS:
        return
    
    from keyboards.admin_keyboards import admin_panel_keyboard
    await message.answer(
        "🔧 Admin Panel",
        reply_markup=admin_panel_keyboard()
    )
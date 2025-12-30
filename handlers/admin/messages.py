"""Admin message handlers"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from states.admin_states import AdminStates
from config import QUESTION_ADMIN_GROUP_ID
from services.category_service import CategoryService
from utils.admin_helpers import is_admin
from services.student_service import StudentService
from keyboards.admin_keyboards import admin_panel_keyboard

router = Router()

category_service = CategoryService()
student_service = StudentService()


@router.message(F.text == "/admin")
async def admin_panel(message: Message):
    """Admin panel"""
    if not is_admin(message.from_user.id):
        return
    
    await message.answer(
        "🔧 Admin Panel",
        reply_markup=admin_panel_keyboard()
    )


@router.message(AdminStates.waiting_category_name)
async def process_new_category(message: Message, state: FSMContext):
    """Process new category name"""
    if not is_admin(message.from_user.id):
        return
    
    category_name = message.text.strip()
    
    is_valid, error = category_service.create_category(category_name)
    if is_valid:
        await message.answer(
            f"✅ Kategoriya '{category_name}' muvaffaqiyatli qo'shildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📂 Kategoriyalarga qaytish", callback_data="list_categories")]
            ])
        )
        await state.clear()
    else:
        await message.answer(f"❌ {error}")


@router.message(AdminStates.waiting_category_edit)
async def process_edit_category(message: Message, state: FSMContext):
    """Process edit category"""
    if not is_admin(message.from_user.id):
        return
    
    data = await state.get_data()
    cat_id = data.get("editing_category_id")
    new_name = message.text.strip()
    
    is_valid, error = category_service.update_category_name(cat_id, new_name)
    if is_valid:
        await message.answer(
            f"✅ Kategoriya nomi '{new_name}' ga o'zgartirildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📂 Kategoriyalarga qaytish", callback_data="list_categories")]
            ])
        )
        await state.clear()
    else:
        await message.answer(f"❌ {error}")


@router.message(F.chat.id == QUESTION_ADMIN_GROUP_ID, F.reply_to_message)
async def admin_reply_to_student(message: Message):
    """Admin guruhda student xabariga reply qilganda"""
    if not is_admin(message.from_user.id):
        return
    
    # Reply qilingan xabarni topish
    replied_message = message.reply_to_message
    if not replied_message:
        return
    
    # Database'dan student message'ni topish
    student_message = student_service.get_message_by_group_id(replied_message.message_id)
    
    if not student_message:
        await message.answer("⚠️ Bu xabar database'da topilmadi. Lekin javob guruhda qoldirildi.")
        return
    
    student_user_id, student_name, group_number = student_message
    
    # Student'ga javob yuborish
    reply_text = (
        f"📚 Sizning murojaatingizga javob:\n\n"
        f"{message.text}\n\n"
        f"💬 Mas'ul xodim javobi"
    )
    
    try:
        await message.bot.send_message(
            chat_id=student_user_id,
            text=reply_text
        )
        await message.reply("✅ Javob o'quvchiga yuborildi!")
    except Exception as e:
        await message.reply(f"❌ Javob yuborishda xatolik: {str(e)}")


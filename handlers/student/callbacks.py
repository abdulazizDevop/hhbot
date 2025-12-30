"""Student callback handlers"""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.student_states import StudentStates
from data.languages import get_text
from services.user_service import UserService
from services.student_service import StudentService
from services.category_service import CategoryService
from config import QUESTION_ADMIN_GROUP_ID

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
student_service = StudentService()
category_service = CategoryService()


@router.callback_query(F.data == "student_send")
async def student_start(callback: CallbackQuery, state: FSMContext):
    """Start student message flow"""
    language = user_service.get_user_language(callback.from_user.id)
    await state.update_data(language=language)
    await state.set_state(StudentStates.name)
    
    await callback.message.answer(
        get_text("enter_student_name", language),
        reply_markup=ReplyKeyboardRemove()
    )
    try:
        await callback.message.delete()
    except Exception:
        pass


@router.callback_query(F.data.startswith("student_dir_"), StudentStates.direction)
async def student_direction_select(callback: CallbackQuery, state: FSMContext):
    """Select student direction"""
    data = await state.get_data()
    language = data.get("language", "uz")
    cat_id = int(callback.data.split("_")[2])
    
    categories = category_service.get_all_categories()
    name = next((n for i, n in categories if i == cat_id), None)
    
    if not name:
        await callback.answer("Topilmadi")
        return
    
    await state.update_data(student_direction=name)
    await state.set_state(StudentStates.group_number)
    await callback.message.edit_text(get_text("enter_student_group", language))


@router.callback_query(F.data.in_(["student_type_suggest", "student_type_complaint"]), StudentStates.type)
async def student_type(callback: CallbackQuery, state: FSMContext):
    """Select student message type"""
    data = await state.get_data()
    language = data.get("language", "uz")
    type_value = "suggest" if callback.data.endswith("suggest") else "complaint"
    
    await state.update_data(student_type=type_value)
    await state.set_state(StudentStates.message)
    await callback.message.edit_text(get_text("enter_student_message", language))


@router.callback_query(F.data == "confirm_ad", StudentStates.confirm)
async def student_confirm(callback: CallbackQuery, state: FSMContext):
    """Confirm student message"""
    data = await state.get_data()
    language = data.get("language", "uz")
    type_label = get_text(
        "student_type_suggest", language
    ) if data.get("student_type") == "suggest" else get_text("student_type_complaint", language)
    
    raw_username = getattr(callback.from_user, "username", None)
    username_line = f"@{raw_username}" if raw_username else "None"
    user_id = callback.from_user.id
    
    text = (
        f"📚 Ustudy o'quvchi xabari\n\n"
        f"👤 Username: {username_line}\n"
        f"🆔 User ID: {user_id}\n"
        f"👤 Ism: {data.get('student_name')}\n"
        f"💼 Yo'nalish: {data.get('student_direction')}\n"
        f"📚 Guruh: {data.get('student_group')}\n"
        f"🏷 Tur: {type_label}\n"
        f"📝 Matn: {data.get('student_message')}"
    )
    
    try:
        sent_message = await callback.bot.send_message(QUESTION_ADMIN_GROUP_ID, text)
        await callback.message.edit_text(get_text("student_message_sent", language))
        
        student_service.create_message(
            user_id=user_id,
            message_id=sent_message.message_id,
            group_message_id=sent_message.message_id,
            name=data.get('student_name'),
            direction=data.get('student_direction'),
            group_number=data.get('student_group'),
            message_type=data.get('student_type'),
            message_text=data.get('student_message')
        )
    except Exception as e:
        logger.error(f"Student message yuborishda xatolik: {str(e)}")
        await callback.message.edit_text(f"Xabarni yuborishda xatolik: {str(e)}")
    
    await state.clear()


@router.callback_query(F.data == "cancel_ad", StudentStates.confirm)
async def student_cancel(callback: CallbackQuery, state: FSMContext):
    """Cancel student message"""
    data = await state.get_data()
    language = data.get("language", "uz")
    await callback.message.edit_text(get_text("ad_cancelled", language))
    await state.clear()


"""Student message handlers"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from states.student_states import StudentStates
from data.languages import get_text
from keyboards.student_keyboards import (
    student_type_keyboard,
    student_confirmation_keyboard,
    student_directions_keyboard
)
from services.student_service import StudentService

router = Router()
student_service = StudentService()


@router.message(StudentStates.name)
async def student_name(message: Message, state: FSMContext):
    """Process student name"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    is_valid, error = student_service.validator.validate_text_length(message.text, 2)
    if not is_valid:
        await message.answer(error or get_text("enter_student_name", language))
        return
    
    await state.update_data(student_name=message.text)
    await state.set_state(StudentStates.direction)
    await message.answer(
        get_text("enter_student_direction", language),
        reply_markup=student_directions_keyboard()
    )


@router.message(StudentStates.direction)
async def student_direction(message: Message, state: FSMContext):
    """Fallback for direction - only inline selection allowed"""
    data = await state.get_data()
    language = data.get("language", "uz")
    await message.answer(
        get_text("enter_student_direction", language),
        reply_markup=student_directions_keyboard()
    )


@router.message(StudentStates.group_number)
async def student_group_number(message: Message, state: FSMContext):
    """Process student group number"""
    data = await state.get_data()
    language = data.get("language", "uz")
    group = message.text.strip()
    
    is_valid, error = student_service.validator.validate_text_length(group, 2)
    if not is_valid:
        await message.answer(error or get_text("enter_student_group", language))
        return
    
    await state.update_data(student_group=group)
    await state.set_state(StudentStates.type)
    await message.answer(
        get_text("enter_student_type", language),
        reply_markup=student_type_keyboard(language)
    )


@router.message(StudentStates.type)
async def student_type_text(message: Message, state: FSMContext):
    """Fallback for type - text input"""
    data = await state.get_data()
    language = data.get("language", "uz")
    text = (message.text or "").strip().lower()
    
    if text in ["taklif", "предложение"]:
        type_value = "suggest"
    elif text in ["shikoyat", "жалоба"]:
        type_value = "complaint"
    else:
        await message.answer(get_text("enter_student_type", language))
        return
    
    await state.update_data(student_type=type_value)
    await state.set_state(StudentStates.message)
    await message.answer(get_text("enter_student_message", language))


@router.message(StudentStates.message)
async def student_message(message: Message, state: FSMContext):
    """Process student message"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    is_valid, error = student_service.validator.validate_text_length(message.text, 10)
    if not is_valid:
        await message.answer(error or get_text("enter_student_message", language))
        return
    
    await state.update_data(student_message=message.text)
    await state.set_state(StudentStates.confirm)
    
    # Review
    d = await state.get_data()
    type_label = get_text(
        "student_type_suggest", language
    ) if d.get("student_type") == "suggest" else get_text("student_type_complaint", language)
    
    review = (
        f"{get_text('student_review', language)}\n\n"
        f"👤 {get_text('label_name', language)}: {d.get('student_name')}\n"
        f"💼 {get_text('label_direction', language)}: {d.get('student_direction')}\n"
        f"📚 {get_text('label_group', language)}: {d.get('student_group')}\n"
        f"🏷 {get_text('label_type', language)}: {type_label}\n"
        f"📝 {get_text('label_message', language)}: {d.get('student_message')}"
    )
    await message.answer(review, reply_markup=student_confirmation_keyboard(language))


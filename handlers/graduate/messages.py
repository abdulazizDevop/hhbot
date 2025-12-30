"""Graduate message handlers"""
import os
import json
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.graduate_states import GraduateStates
from data.languages import get_text
from keyboards.base import (
    contact_keyboard, regions_keyboard, categories_keyboard,
    confirmation_keyboard
)
from keyboards.graduate_keyboards import graduate_main_menu
from services.user_service import UserService
from services.ad_service import AdService
from services.validation_service import ValidationService
from services.category_service import CategoryService
from utils.text_formatters import format_ad_text
from utils.validators import validate_phone, clean_phone
from utils.constants import MIN_AGE, MAX_AGE, MAX_FILE_SIZE, ALLOWED_FILE_FORMATS
from config import RESUME_FOLDER

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
ad_service = AdService()
validator = ValidationService()
category_service = CategoryService()


@router.message(F.text & F.text.func(lambda text: text and text.startswith("🎓") and any(
    keyword in text for keyword in ["E'lon yaratish", "Создать объявление"]
)))
async def start_create_ad_graduate(message: Message, state: FSMContext):
    """Start creating graduate ad"""
    logger.info(f"🎓 GRADUATE E'lon yaratish: {message.from_user.id}")
    
    is_valid, language = user_service.check_user_role(message.from_user.id, "graduate")
    if not is_valid:
        logger.warning(f"🎓 GRADUATE Ruxsat yo'q")
        await message.answer("Sizda ruxsat yo'q!")
        return
    
    await state.update_data(language=language, role="graduate")
    await state.set_state(GraduateStates.name)
    
    await message.answer(
        get_text("enter_name", language),
        reply_markup=ReplyKeyboardRemove()
    )


@router.message(GraduateStates.name)
async def process_name(message: Message, state: FSMContext):
    """Process name"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(name=message.text)
    await state.set_state(GraduateStates.age)
    await message.answer(get_text("enter_age_gr", language), reply_markup=ReplyKeyboardRemove())


@router.message(GraduateStates.age)
async def process_age(message: Message, state: FSMContext):
    """Process age"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    is_valid, error = validator.validate_age(message.text, MIN_AGE, MAX_AGE)
    if not is_valid:
        await message.answer(error or f"{get_text('enter_age_gr', language)} ({MIN_AGE}-{MAX_AGE})")
        return
    
    await state.update_data(age=message.text)
    await state.set_state(GraduateStates.technologies)
    await message.answer(get_text("enter_technologies", language), reply_markup=ReplyKeyboardRemove())


@router.message(GraduateStates.technologies)
async def process_technologies(message: Message, state: FSMContext):
    """Process technologies"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(technologies=message.text)
    await state.set_state(GraduateStates.contact)
    await message.answer(
        get_text("enter_contact", language),
        reply_markup=contact_keyboard(language)
    )


@router.message(GraduateStates.contact)
async def process_contact(message: Message, state: FSMContext):
    """Process contact"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    if message.contact:
        phone = clean_phone(message.contact.phone_number)
    else:
        phone = clean_phone(message.text)
        if not validate_phone(phone):
            await message.answer(
                "Iltimos, to'g'ri telefon raqam kiriting:" if language == "uz" 
                else "Пожалуйста, введите правильный номер телефона:"
            )
            return
    
    await state.update_data(contact=phone)
    await state.set_state(GraduateStates.region)
    await message.answer(
        get_text("enter_region", language),
        reply_markup=regions_keyboard(language)
    )


@router.message(GraduateStates.price)
async def process_price(message: Message, state: FSMContext):
    """Process price"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(price=message.text)
    await state.set_state(GraduateStates.profession)
    await message.answer(
        get_text("enter_profession", language),
        reply_markup=categories_keyboard()
    )


@router.message(GraduateStates.contact_time)
async def process_contact_time(message: Message, state: FSMContext):
    """Process contact time"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(contact_time=message.text)
    await state.set_state(GraduateStates.goal)
    await message.answer(get_text("enter_goal", language))


@router.message(GraduateStates.goal)
async def process_goal(message: Message, state: FSMContext):
    """Process goal"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(goal=message.text)
    await state.set_state(GraduateStates.resume)
    await message.answer(get_text("enter_resume", language))


@router.message(GraduateStates.resume, F.document)
async def process_resume(message: Message, state: FSMContext):
    """Process resume file"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    # File size check
    if message.document.file_size > MAX_FILE_SIZE:
        await message.answer(f"Fayl hajmi {MAX_FILE_SIZE//1024//1024}MB dan kichik bo'lishi kerak!")
        return
    
    # File format check
    file_name = message.document.file_name.lower()
    if not any(file_name.endswith(fmt) for fmt in ALLOWED_FILE_FORMATS):
        await message.answer(f"Faqat {', '.join(ALLOWED_FILE_FORMATS)} formatdagi fayllar qabul qilinadi!")
        return
    
    # Download file
    file_info = await message.bot.get_file(message.document.file_id)
    file_path = os.path.join(RESUME_FOLDER, f"{message.document.file_id}_{file_name}")
    await message.bot.download_file(file_info.file_path, file_path)
    
    # Create ad
    ad_data = {
        "name": data.get("name"),
        "age": data.get("age"),
        "technologies": data.get("technologies"),
        "contact": data.get("contact"),
        "region": data.get("region"),
        "price": data.get("price"),
        "profession": data.get("profession"),
        "contact_time": data.get("contact_time"),
        "goal": data.get("goal")
    }
    
    ad_id = ad_service.create_ad(
        user_id=message.from_user.id,
        ad_type="graduate",
        data=ad_data,
        file_id=message.document.file_id,
        file_path=file_path,
        status="draft"
    )
    
    await state.update_data(ad_id=ad_id)
    await state.set_state(GraduateStates.confirm)
    
    # Show confirmation
    ad_text = format_ad_text(ad_data, "graduate", language)
    await message.answer(
        f"{get_text('confirm_ad', language)}\n\n{ad_text}",
        reply_markup=confirmation_keyboard(language),
        parse_mode="HTML"
    )


@router.message(GraduateStates.resume)
async def resume_not_document(message: Message, state: FSMContext):
    """Resume is not a document"""
    data = await state.get_data()
    language = data.get("language", "uz")
    await message.answer(get_text("enter_resume", language))


@router.message(F.text & F.text.func(lambda text: text and text.startswith("🎓") and any(
    keyword in text for keyword in ["Mening e'lonlarim", "Мои объявления"]
)))
async def my_ads_message_graduate(message: Message, state: FSMContext):
    """My ads message handler"""
    logger.info(f"🎓 GRADUATE My ads: {message.from_user.id}")
    
    is_valid, language = user_service.check_user_role(message.from_user.id, "graduate")
    if not is_valid:
        await message.answer("Sizda ruxsat yo'q!")
        return
    
    ads = ad_service.get_user_ads(message.from_user.id)
    
    if not ads:
        await message.answer(
            get_text("no_ads", language),
            reply_markup=graduate_main_menu(language)
        )
        return
    
    await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
    from keyboards.graduate_keyboards import my_ads_keyboard
    await message.answer(
        get_text("ads_list", language),
        reply_markup=my_ads_keyboard(ads, language)
    )


@router.message(GraduateStates.edit_field)
async def process_edit_field(message: Message, state: FSMContext):
    """Process edit field"""
    data = await state.get_data()
    language = data.get("language", "uz")
    field_name = data.get("edit_field")
    ad_id = data.get("ad_id")
    
    # Get current ad
    ad = ad_service.get_ad(ad_id)
    if not ad:
        await message.answer("E'lon topilmadi!")
        return
    
    ad_data = json.loads(ad[4])
    old_value = ad_data.get(field_name, "")
    
    # Validate new value
    new_value = message.text
    
    if field_name == "contact":
        if message.contact:
            new_value = clean_phone(message.contact.phone_number)
        else:
            new_value = clean_phone(message.text)
            if not validate_phone(new_value):
                await message.answer("Iltimos, to'g'ri telefon raqam kiriting:")
                return
    elif field_name == "age":
        is_valid, error = validator.validate_age(new_value, MIN_AGE, MAX_AGE)
        if not is_valid:
            await message.answer(error or f"{get_text('enter_age_gr', language)} ({MIN_AGE}-{MAX_AGE})")
            return
    
    # Update field
    success = ad_service.update_ad_field(ad_id, field_name, old_value, new_value, message.from_user.id)
    
    if success:
        await message.answer(get_text("field_updated", language))
        
        # Show updated ad
        ad = ad_service.get_ad(ad_id)
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "graduate", language)
        
        await state.update_data(ad_id=ad_id)
        await state.set_state(GraduateStates.confirm)
        await message.answer(
            f"{get_text('confirm_ad', language)}\n\n{ad_text}",
            reply_markup=confirmation_keyboard(language),
            parse_mode="HTML"
        )
    else:
        await message.answer("Xatolik yuz berdi!")


@router.message(GraduateStates.edit_field, F.document)
async def process_edit_resume(message: Message, state: FSMContext):
    """Process edit resume"""
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    # File validation
    if message.document.file_size > MAX_FILE_SIZE:
        await message.answer(f"Fayl hajmi {MAX_FILE_SIZE//1024//1024}MB dan kichik bo'lishi kerak!")
        return
    
    file_name = message.document.file_name.lower()
    if not any(file_name.endswith(fmt) for fmt in ALLOWED_FILE_FORMATS):
        await message.answer(f"Faqat {', '.join(ALLOWED_FILE_FORMATS)} formatdagi fayllar qabul qilinadi!")
        return
    
    # Download file
    file_info = await message.bot.get_file(message.document.file_id)
    file_path = os.path.join(RESUME_FOLDER, f"{message.document.file_id}_{file_name}")
    await message.bot.download_file(file_info.file_path, file_path)
    
    # Update ad
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        old_file_id = ad[5]
        success = ad_service.update_ad_data(ad_id, ad_data, message.document.file_id, file_path)
        
        if success:
            await message.answer(get_text("field_updated", language))
            
            ad_text = format_ad_text(ad_data, "graduate", language)
            await state.update_data(ad_id=ad_id)
            await state.set_state(GraduateStates.confirm)
            await message.answer(
                f"{get_text('confirm_ad', language)}\n\n{ad_text}",
                reply_markup=confirmation_keyboard(language),
                parse_mode="HTML"
            )
        else:
            await message.answer("Xatolik yuz berdi!")


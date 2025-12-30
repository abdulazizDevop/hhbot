"""Employer message handlers"""
import json
import logging
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove

from states.employer_states import EmployerStates
from data.languages import get_text
from keyboards.base import categories_keyboard, confirmation_keyboard
from keyboards.employer_keyboards import employer_main_menu
from services.user_service import UserService
from services.ad_service import AdService
from services.validation_service import ValidationService
from services.category_service import CategoryService
from utils.text_formatters import format_ad_text
from utils.constants import MIN_AGE_EMPLOYER, MAX_AGE

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
ad_service = AdService()
validator = ValidationService()
category_service = CategoryService()


@router.message(F.text & F.text.func(lambda text: text and text.startswith("👔") and any(
    keyword in text for keyword in ["E'lon yaratish", "Создать объявление"]
)))
async def start_create_ad_employer(message: Message, state: FSMContext):
    """Start creating employer ad"""
    logger.info(f"👔 EMPLOYER E'lon yaratish: {message.from_user.id}")
    
    is_valid, language = user_service.check_user_role(message.from_user.id, "employer")
    if not is_valid:
        logger.warning(f"👔 EMPLOYER Ruxsat yo'q")
        await message.answer("Sizda ruxsat yo'q!")
        return
    
    await state.update_data(language=language, role="employer")
    await state.set_state(EmployerStates.company)
    await message.answer(get_text("enter_company", language), reply_markup=ReplyKeyboardRemove())


@router.message(EmployerStates.company)
async def process_company(message: Message, state: FSMContext):
    """Process company name"""
    is_valid, error = validator.validate_text_length(message.text, 2)
    if not is_valid:
        await message.answer(error or "Iltimos, to'g'ri kompaniya nomini kiriting (kamida 2 belgi):")
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(company=message.text)
    await state.set_state(EmployerStates.name)
    await message.answer(get_text("enter_name", language))


@router.message(EmployerStates.name)
async def process_name(message: Message, state: FSMContext):
    """Process name"""
    is_valid, error = validator.validate_text_length(message.text, 3)
    if not is_valid:
        await message.answer(error or "Iltimos, to'g'ri ism kiriting (kamida 3 belgi):")
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(name=message.text)
    await state.set_state(EmployerStates.age)
    await message.answer(get_text("enter_age_emp", language))


@router.message(EmployerStates.age)
async def process_age(message: Message, state: FSMContext):
    """Process age"""
    is_valid, error = validator.validate_age(message.text, MIN_AGE_EMPLOYER, MAX_AGE)
    if not is_valid:
        data = await state.get_data()
        language = data.get("language", "uz")
        await message.answer(error or get_text("enter_age_emp", language))
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(age=message.text)
    await state.set_state(EmployerStates.category)
    await message.answer(
        get_text("enter_job_category", language),
        reply_markup=categories_keyboard()
    )


@router.message(EmployerStates.gender)
async def process_gender(message: Message, state: FSMContext):
    """Process gender"""
    is_valid, error = validator.validate_gender(message.text)
    if not is_valid:
        await message.answer(error or "Iltimos, to'g'ri jinsni kiriting (erkak, ayol, farqi yo'q):")
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(gender=message.text or "farqi yo'q")
    await state.set_state(EmployerStates.experience)
    await message.answer(get_text("enter_experience", language), reply_markup=ReplyKeyboardRemove())


@router.message(EmployerStates.experience)
async def process_experience(message: Message, state: FSMContext):
    """Process experience"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(experience=message.text)
    await state.set_state(EmployerStates.work_days)
    await message.answer(get_text("enter_work_days", language))


@router.message(EmployerStates.work_days)
async def process_work_days(message: Message, state: FSMContext):
    """Process work days"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(work_days=message.text)
    await state.set_state(EmployerStates.work_hours)
    await message.answer(get_text("enter_work_hours", language))


@router.message(EmployerStates.work_hours)
async def process_work_hours(message: Message, state: FSMContext):
    """Process work hours"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(work_hours=message.text)
    await state.set_state(EmployerStates.location)
    await message.answer(get_text("enter_location", language))


@router.message(EmployerStates.location)
async def process_location(message: Message, state: FSMContext):
    """Process location"""
    is_valid, error = validator.validate_text_length(message.text, 5)
    if not is_valid:
        await message.answer(error or "Iltimos, to'g'ri manzil kiriting (kamida 5 belgi):")
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(location=message.text)
    await state.set_state(EmployerStates.salary)
    await message.answer(get_text('enter_salary', language))


@router.message(EmployerStates.salary)
async def process_salary(message: Message, state: FSMContext):
    """Process salary"""
    is_valid, error = validator.validate_salary(message.text)
    if not is_valid:
        await message.answer(error or "Iltimos, to'g'ri maosh kiriting (raqam yoki $ bilan):")
        return
    
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(salary=message.text)
    await state.set_state(EmployerStates.requirements)
    await message.answer(get_text("enter_requirements", language))


@router.message(EmployerStates.requirements)
async def process_requirements(message: Message, state: FSMContext):
    """Process requirements"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    requirements_text = message.text if message.text else "Yo'q"
    await state.update_data(requirements=requirements_text)
    
    # Create ad (draft)
    ad_data = {
        "company": data.get("company"),
        "name": data.get("name"),
        "age": data.get("age"),
        "category": data.get("category"),
        "gender": data.get("gender"),
        "experience": data.get("experience"),
        "work_days": data.get("work_days"),
        "work_hours": data.get("work_hours"),
        "location": data.get("location"),
        "salary": data.get("salary"),
        "requirements": requirements_text
    }
    
    ad_id = ad_service.create_ad(
        user_id=message.from_user.id,
        ad_type="employer",
        data=ad_data,
        status="draft"
    )
    
    await state.update_data(ad_id=ad_id)
    await state.set_state(EmployerStates.confirm)
    
    # Show confirmation
    ad_text = format_ad_text(ad_data, "employer", language)
    await message.answer(
        f"{get_text('confirm_ad', language)}\n\n{ad_text}",
        reply_markup=confirmation_keyboard(language),
        parse_mode="HTML"
    )


@router.message(EmployerStates.edit_field)
async def process_edit_field(message: Message, state: FSMContext):
    """Process edit field"""
    data = await state.get_data()
    language = data.get("language", "uz")
    field_name = data.get("edit_field")
    ad_id = data.get("ad_id")
    
    # Validate
    new_value = message.text
    
    if field_name == "company":
        is_valid, error = validator.validate_text_length(new_value, 2)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri kompaniya nomini kiriting (kamida 2 belgi):")
            return
    elif field_name == "name":
        is_valid, error = validator.validate_text_length(new_value, 3)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri ism kiriting (kamida 3 belgi):")
            return
    elif field_name == "age":
        is_valid, error = validator.validate_age(new_value, MIN_AGE_EMPLOYER, MAX_AGE)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri yosh kiriting (18-65):")
            return
    elif field_name == "gender":
        is_valid, error = validator.validate_gender(new_value)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri jinsni kiriting (erkak, ayol, farqi yo'q):")
            return
    elif field_name == "salary":
        is_valid, error = validator.validate_salary(new_value)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri maosh kiriting (raqam yoki $ bilan):")
            return
    elif field_name == "location":
        is_valid, error = validator.validate_text_length(new_value, 5)
        if not is_valid:
            await message.answer(error or "Iltimos, to'g'ri manzil kiriting (kamida 5 belgi):")
            return
    
    # Get current ad
    ad = ad_service.get_ad(ad_id)
    if not ad:
        await message.answer("E'lon topilmadi!")
        return
    
    ad_data = json.loads(ad[4])
    old_value = ad_data.get(field_name, "")
    
    # Update field
    success = ad_service.update_ad_field(ad_id, field_name, old_value, new_value, message.from_user.id)
    
    if success:
        await message.answer(get_text("field_updated", language))
        
        # Show updated ad
        ad = ad_service.get_ad(ad_id)
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "employer", language)
        
        await state.update_data(ad_id=ad_id)
        await state.set_state(EmployerStates.confirm)
        await message.answer(
            f"{get_text('confirm_ad', language)}\n\n{ad_text}",
            reply_markup=confirmation_keyboard(language),
            parse_mode="HTML"
        )
    else:
        await message.answer("Xatolik yuz berdi!")


@router.message(F.text & F.text.func(lambda text: text and text.startswith("👔") and any(
    keyword in text for keyword in ["Mening e'lonlarim", "Мои объявления"]
)))
async def my_ads_employer(message: Message, state: FSMContext):
    """My ads message handler"""
    logger.info(f"👔 EMPLOYER My ads: {message.from_user.id}")
    
    is_valid, language = user_service.check_user_role(message.from_user.id, "employer")
    if not is_valid:
        await message.answer("Sizda ruxsat yo'q!")
        return
    
    ads = ad_service.get_user_ads(message.from_user.id)
    
    if not ads:
        await message.answer(
            get_text("no_ads", language),
            reply_markup=employer_main_menu(language)
        )
        return
    
    await message.answer("⏳", reply_markup=ReplyKeyboardRemove())
    from keyboards.graduate_keyboards import my_ads_keyboard
    await message.answer(
        get_text("ads_list", language),
        reply_markup=my_ads_keyboard(ads, language)
    )


@router.message(F.text & F.text.func(lambda text: text == get_text("browse_by_category", "uz") or text == get_text("browse_by_category", "ru")))
async def browse_by_category_entry(message: Message, state: FSMContext):
    """Browse by category entry"""
    language = user_service.get_user_language(message.from_user.id)
    from keyboards.employer_keyboards import browse_categories_keyboard
    await message.answer(
        get_text("select_category", language),
        reply_markup=browse_categories_keyboard()
    )


@router.message(F.text & F.text.func(lambda text: text and text in [
    get_text("contact_admin", "uz"), get_text("contact_admin", "ru")
]))
async def contact_admin(message: Message, state: FSMContext):
    """Contact admin"""
    is_valid, language = user_service.check_user_role(message.from_user.id, "employer")
    if not is_valid:
        await message.answer("Sizda ruxsat yo'q!")
        return
    
    from config import ADMIN_IDS
    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    
    admin_id = ADMIN_IDS[0] if ADMIN_IDS else None
    if admin_id:
        admin_link = f"tg://user?id={admin_id}"
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="👨‍💼 Admin", url=admin_link)]
        ])
        await message.answer(get_text("contact_admin", language), reply_markup=keyboard)
    else:
        await message.answer(get_text("contact_admin", language))


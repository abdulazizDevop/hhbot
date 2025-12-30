"""Employer callback handlers"""
import json
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.exceptions import TelegramBadRequest

from states.employer_states import EmployerStates
from data.languages import get_text
from keyboards.base import categories_keyboard, confirmation_keyboard
from keyboards.employer_keyboards import (
    employer_main_menu, edit_fields_keyboard_employer,
    ad_actions_keyboard_employer
)
from keyboards.graduate_keyboards import my_ads_keyboard
from keyboards.admin_keyboards import admin_moderation_keyboard
from services.user_service import UserService
from services.ad_service import AdService
from services.category_service import CategoryService
from services.validation_service import ValidationService
from utils.text_formatters import format_ad_text, get_status_text, format_date
from config import VACANCY_ADMIN_GROUP_ID

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
ad_service = AdService()
category_service = CategoryService()
validator = ValidationService()


@router.callback_query(F.data.startswith("category_"), EmployerStates.category)
async def process_category(callback: CallbackQuery, state: FSMContext):
    """Process category selection"""
    try:
        category_id = int(callback.data.split("_")[1])
        data = await state.get_data()
        language = data.get("language", "uz")
        
        categories = category_service.get_all_categories()
        category_name = next((name for id, name in categories if id == category_id), "")
        
        if not category_name:
            await callback.message.answer("Kategoriya topilmadi!")
            return
        
        await state.update_data(category=category_name)
        await state.set_state(EmployerStates.gender)
        await callback.message.edit_text(get_text("enter_gender", language))
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == "confirm_ad", EmployerStates.confirm)
async def confirm_ad(callback: CallbackQuery, state: FSMContext):
    """Confirm ad and send to admin"""
    try:
        data = await state.get_data()
        language = data.get("language", "uz")
        ad_id = data.get("ad_id")
        
        # Update status to pending
        if not ad_service.update_ad_status(ad_id, "pending", callback.from_user.id):
            await callback.answer("E'lon topilmadi yoki statusni yangilashda xatolik!")
            return
        
        # Send to admin
        ad = ad_service.get_ad(ad_id)
        if ad:
            ad_data = json.loads(ad[4])
            ad_text = format_ad_text(ad_data, "employer", language)
            
            await callback.bot.send_message(
                chat_id=VACANCY_ADMIN_GROUP_ID,
                text=f"💼 Yangi ish e'loni #{ad_id}\n\n{ad_text}",
                reply_markup=admin_moderation_keyboard(ad_id),
                parse_mode="HTML"
            )
        
        await callback.message.answer(
            get_text("ad_created", language),
            reply_markup=employer_main_menu(language)
        )
        await callback.message.delete()
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == "cancel_ad", EmployerStates.confirm)
async def cancel_ad(callback: CallbackQuery, state: FSMContext):
    """Cancel ad"""
    try:
        data = await state.get_data()
        language = data.get("language", "uz")
        ad_id = data.get("ad_id")
        
        if not ad_service.update_ad_status(ad_id, "cancelled", callback.from_user.id):
            await callback.message.answer("E'lon topilmadi!")
            return
        
        await callback.message.answer(
            get_text("ad_cancelled", language),
            reply_markup=employer_main_menu(language)
        )
        await callback.message.delete()
        await state.clear()
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == "edit_ad", EmployerStates.confirm)
async def edit_ad(callback: CallbackQuery, state: FSMContext):
    """Start editing ad"""
    try:
        data = await state.get_data()
        language = data.get("language", "uz")
        
        await state.set_state(EmployerStates.edit)
        await callback.message.edit_text(
            get_text("select_edit_field", language),
            reply_markup=edit_fields_keyboard_employer(language)
        )
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("emp_view_"))
async def view_ad_employer(callback: CallbackQuery, state: FSMContext):
    """View ad"""
    try:
        logger.info(f"EMPLOYER emp_view triggered: {callback.data} by {callback.from_user.id}")
        ad_id = int(callback.data.split("_")[2])
        
        is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
        if not is_valid:
            await callback.answer("Sizda ruxsat yo'q!")
            return
        
        ad = ad_service.get_ad(ad_id)
        
        if not ad or ad[1] != callback.from_user.id:
            await callback.answer("E'lon topilmadi!")
            return
        
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, ad[2], language)
        status_text = get_status_text(ad[3], language)
        created_date = format_date(ad[7])
        
        full_text = f"{ad_text}\n\n📊 <b>Status:</b> {status_text}\n📅 <b>Yaratildi:</b> {created_date}"
        
        await callback.message.edit_text(
            full_text,
            reply_markup=ad_actions_keyboard_employer(ad_id, ad[3], language),
            parse_mode="HTML"
        )
    except Exception as e:
        await callback.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data == "my_ads_employer")
async def my_ads_callback(callback: CallbackQuery, state: FSMContext):
    """My ads callback"""
    try:
        is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
        if not is_valid:
            await callback.answer("Ruxsat yo'q!")
            return
        
        ads = ad_service.get_user_ads(callback.from_user.id)
        
        if not ads:
            await callback.message.edit_text(
                get_text("no_ads", language),
                reply_markup=employer_main_menu(language)
            )
            return
        
        await callback.message.edit_text(
            get_text("ads_list", language),
            reply_markup=my_ads_keyboard(ads, language)
        )
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("edit_field_"), EmployerStates.edit)
async def select_edit_field(callback: CallbackQuery, state: FSMContext):
    """Select field to edit"""
    try:
        field_name = callback.data.split("edit_field_")[1]
        data = await state.get_data()
        language = data.get("language", "uz")
        
        await state.update_data(edit_field=field_name)
        
        if field_name == "category":
            await state.set_state(EmployerStates.edit_field)
            await callback.message.edit_text(
                get_text("enter_job_category", language),
                reply_markup=categories_keyboard()
            )
        else:
            await state.set_state(EmployerStates.edit_field)
            
            field_texts = {
                "company": "enter_company",
                "name": "enter_name",
                "age": "enter_age_emp",
                "gender": "enter_gender",
                "experience": "enter_experience",
                "work_days": "enter_work_days",
                "work_hours": "enter_work_hours",
                "location": "enter_location",
                "salary": "enter_salary",
                "requirements": "enter_requirements"
            }
            
            text_key = field_texts.get(field_name, "enter_new_value")
            await callback.message.edit_text(get_text(text_key, language))
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("category_"), EmployerStates.edit_field)
async def process_edit_category(callback: CallbackQuery, state: FSMContext):
    """Process edit category"""
    try:
        category_id = int(callback.data.split("_")[1])
        data = await state.get_data()
        language = data.get("language", "uz")
        ad_id = data.get("ad_id")
        field_name = data.get("edit_field")
        
        categories = category_service.get_all_categories()
        new_value = next((name for id, name in categories if id == category_id), "")
        
        if not new_value:
            await callback.message.answer("Kategoriya topilmadi!")
            return
        
        ad = ad_service.get_ad(ad_id)
        if not ad:
            await callback.message.answer("E'lon topilmadi!")
            return
        
        ad_data = json.loads(ad[4])
        old_value = ad_data.get(field_name, "")
        
        success = ad_service.update_ad_field(ad_id, field_name, old_value, new_value, callback.from_user.id)
        
        if success:
            await callback.message.answer(get_text("field_updated", language))
            
            ad = ad_service.get_ad(ad_id)
            ad_data = json.loads(ad[4])
            ad_text = format_ad_text(ad_data, "employer", language)
            
            await state.update_data(ad_id=ad_id)
            await state.set_state(EmployerStates.confirm)
            await callback.message.answer(
                f"{get_text('confirm_ad', language)}\n\n{ad_text}",
                reply_markup=confirmation_keyboard(language),
                parse_mode="HTML"
            )
        else:
            await callback.message.answer("Xatolik yuz berdi!")
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")
    finally:
        try:
            await callback.message.delete()
        except Exception:
            pass


@router.callback_query(F.data == "back_to_confirm")
async def back_to_confirm(callback: CallbackQuery, state: FSMContext):
    """Back to confirm"""
    try:
        data = await state.get_data()
        language = data.get("language", "uz")
        ad_id = data.get("ad_id")
        
        ad = ad_service.get_ad(ad_id)
        if not ad:
            await callback.message.answer("E'lon topilmadi!")
            return
        
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "employer", language)
        
        await state.set_state(EmployerStates.confirm)
        await callback.message.edit_text(
            f"{get_text('confirm_ad', language)}\n\n{ad_text}",
            reply_markup=confirmation_keyboard(language),
            parse_mode="HTML"
        )
    except TelegramBadRequest:
        await callback.message.answer("Xabar yangilashda xatolik! Qaytadan urinib ko'ring.")
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("emp_edit_draft_"))
async def edit_draft_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Edit draft ad"""
    try:
        ad_id = int(callback.data.split("_")[3])
        
        is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
        if not is_valid:
            await callback.answer("Sizda ruxsat yo'q!")
            return
        
        ad = ad_service.get_ad(ad_id)
        
        if not ad or ad[1] != callback.from_user.id:
            await callback.answer("E'lon topilmadi!")
            return
        
        await state.update_data(ad_id=ad_id, language=language, role="employer")
        await state.set_state(EmployerStates.edit)
        await callback.message.edit_text(
            get_text("select_edit_field", language),
            reply_markup=edit_fields_keyboard_employer(language)
        )
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("emp_confirm_draft_"))
async def confirm_draft_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Confirm draft ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
    if not is_valid:
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad[3] != "draft":
        await callback.answer("Bu e'lon allaqachon yuborilgan!")
        return
    
    # Update status to pending
    if not ad_service.update_ad_status(ad_id, "pending", callback.from_user.id):
        await callback.message.answer("Statusni yangilashda xatolik!")
        return
    
    # Send to admin
    ad_data = json.loads(ad[4])
    ad_text = format_ad_text(ad_data, "employer", language)
    
    await callback.bot.send_message(
        chat_id=VACANCY_ADMIN_GROUP_ID,
        text=f"💼 Yangi ish e'loni #{ad_id}\n\n{ad_text}",
        reply_markup=admin_moderation_keyboard(ad_id),
        parse_mode="HTML"
    )
    
    await callback.message.edit_text(
        get_text("ad_created", language),
        reply_markup=employer_main_menu(language)
    )


@router.callback_query(F.data.startswith("emp_cancel_pending_"))
async def cancel_pending_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Cancel pending ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
    if not is_valid:
        await callback.answer("Ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad[3] != "pending":
        await callback.answer("Bu e'lonni bekor qilib bo'lmaydi!")
        return
    
    if ad_service.update_ad_status(ad_id, "cancelled", callback.from_user.id):
        await callback.message.edit_text(
            f"❌ E'lon #{ad_id} bekor qilindi!",
            reply_markup=employer_main_menu(language)
        )


@router.callback_query(F.data.startswith("emp_edit_pending_"))
async def edit_pending_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Edit pending ad"""
    try:
        ad_id = int(callback.data.split("_")[3])
        
        is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
        if not is_valid:
            await callback.answer("Sizda ruxsat yo'q!")
            return
        
        ad = ad_service.get_ad(ad_id)
        
        if not ad or ad[1] != callback.from_user.id:
            await callback.answer("E'lon topilmadi!")
            return
        
        await state.update_data(ad_id=ad_id, language=language, role="employer")
        await state.set_state(EmployerStates.edit)
        await callback.message.edit_text(
            get_text("select_edit_field", language),
            reply_markup=edit_fields_keyboard_employer(language)
        )
    except Exception as e:
        await callback.message.answer(f"Xatolik yuz berdi: {str(e)}")


@router.callback_query(F.data.startswith("browse_cat_"))
async def browse_category(callback: CallbackQuery, state: FSMContext):
    """Browse category"""
    try:
        cat_id = int(callback.data.split("_")[2])
        categories = category_service.get_all_categories()
        category = next((name for id, name in categories if id == cat_id), None)
        
        if not category:
            await callback.answer("Kategoriya topilmadi!")
            return
        
        language = user_service.get_user_language(callback.from_user.id)
        ads = ad_service.get_approved_ads_by_category(category)
        
        if not ads:
            await callback.message.edit_text(get_text("no_ads_in_category", language).format(category=category))
            return
        
        await callback.message.edit_text(get_text("category_results", language).format(category=category))
        
        for ad in ads[:10]:
            ad_id, user_id, ad_type, status, data, file_id, file_path, created_at, updated_at, approved_at, approved_by = ad
            ad_data = json.loads(data)
            text = format_ad_text(ad_data, ad_type, language)
            
            if ad_type == "graduate" and file_id:
                await callback.bot.send_document(
                    chat_id=callback.from_user.id,
                    document=file_id,
                    caption=text,
                    parse_mode="HTML"
                )
            else:
                await callback.bot.send_message(
                    chat_id=callback.from_user.id,
                    text=text,
                    parse_mode="HTML"
                )
    except Exception as e:
        await callback.answer(f"Xatolik: {str(e)}")


@router.callback_query(F.data.startswith("emp_delete_"))
async def delete_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Delete ad"""
    ad_id = int(callback.data.split("_")[2])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
    if not is_valid:
        await callback.answer("Ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    # Confirmation keyboard
    confirm_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"emp_confirm_delete_{ad_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=f"emp_view_{ad_id}")
        ]
    ])
    
    await callback.message.edit_text(
        f"🗑 E'lonni o'chirish\n\n⚠️ Bu e'lon sizning ro'yxatingizdan o'chib ketadi.\n\nRostdan ham o'chirmoqchimisiz?",
        reply_markup=confirm_keyboard
    )


@router.callback_query(F.data.startswith("emp_confirm_delete_"))
async def confirm_delete_ad_employer(callback: CallbackQuery, state: FSMContext):
    """Confirm delete ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "employer")
    if not is_valid:
        await callback.answer("Ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad_service.update_ad_status(ad_id, "deleted", callback.from_user.id):
        await callback.message.edit_text(
            f"✅ E'lon #{ad_id} muvaffaqiyatli o'chirildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🏠 Asosiy menyu", callback_data="main_menu")]
            ])
        )
    else:
        await callback.answer("❌ O'chirishda xatolik yuz berdi!")


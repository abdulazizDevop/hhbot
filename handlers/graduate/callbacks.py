"""Graduate callback handlers"""
import json
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from states.graduate_states import GraduateStates
from data.languages import get_text
from keyboards.base import (
    regions_keyboard, categories_keyboard, confirmation_keyboard
)
from keyboards.graduate_keyboards import (
    graduate_main_menu, edit_fields_keyboard_graduate,
    my_ads_keyboard, ad_actions_keyboard_graduate
)
from keyboards.admin_keyboards import admin_moderation_keyboard
from services.user_service import UserService
from services.ad_service import AdService
from services.category_service import CategoryService
from utils.text_formatters import format_ad_text, get_status_text, format_date
from config import RESUME_ADMIN_GROUP_ID

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
ad_service = AdService()
category_service = CategoryService()


@router.callback_query(F.data.startswith("region_"), GraduateStates.region)
async def process_region(callback: CallbackQuery, state: FSMContext):
    """Process region selection"""
    region_index = int(callback.data.split("_")[1])
    data = await state.get_data()
    language = data.get("language", "uz")
    
    regions = get_text("regions", language)
    region = regions[region_index]
    
    await state.update_data(region=region)
    await state.set_state(GraduateStates.price)
    
    await callback.message.answer(get_text("enter_price", language))
    await callback.message.delete()


@router.callback_query(F.data.startswith("category_"), GraduateStates.profession)
async def process_profession(callback: CallbackQuery, state: FSMContext):
    """Process profession selection"""
    category_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    language = data.get("language", "uz")
    
    categories = category_service.get_all_categories()
    category_name = next((name for id, name in categories if id == category_id), "")
    
    if not category_name:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    await state.update_data(profession=category_name)
    await state.set_state(GraduateStates.contact_time)
    
    await callback.message.answer(get_text("enter_contact_time", language))
    await callback.message.delete()


@router.callback_query(F.data == "confirm_ad", GraduateStates.confirm)
async def confirm_ad(callback: CallbackQuery, state: FSMContext):
    """Confirm ad and send to admin"""
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    # Update status to pending
    ad_service.update_ad_status(ad_id, "pending", callback.from_user.id)
    
    # Send to admin
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "graduate", language)
        
        if ad[5]:  # file_id exists
            await callback.bot.send_document(
                chat_id=RESUME_ADMIN_GROUP_ID,
                document=ad[5],
                caption=f"📝 Yangi bitiruvchi e'loni #{ad_id}\n\n{ad_text}",
                reply_markup=admin_moderation_keyboard(ad_id),
                parse_mode="HTML"
            )
        else:
            await callback.bot.send_message(
                chat_id=RESUME_ADMIN_GROUP_ID,
                text=f"📝 Yangi bitiruvchi e'loni #{ad_id}\n\n{ad_text}",
                reply_markup=admin_moderation_keyboard(ad_id),
                parse_mode="HTML"
            )
    
    await callback.message.answer(
        get_text("ad_created", language),
        reply_markup=graduate_main_menu(language)
    )
    await callback.message.delete()
    await state.clear()


@router.callback_query(F.data == "cancel_ad", GraduateStates.confirm)
async def cancel_ad(callback: CallbackQuery, state: FSMContext):
    """Cancel ad"""
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    ad_service.update_ad_status(ad_id, "cancelled", callback.from_user.id)
    await callback.message.answer(
        get_text("ad_cancelled", language),
        reply_markup=graduate_main_menu(language)
    )
    await state.clear()
    await callback.message.delete()


@router.callback_query(F.data == "edit_ad", GraduateStates.confirm)
async def edit_ad(callback: CallbackQuery, state: FSMContext):
    """Start editing ad"""
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.set_state(GraduateStates.edit)
    await callback.message.answer(
        get_text("select_edit_field", language),
        reply_markup=edit_fields_keyboard_graduate(language)
    )


@router.callback_query(F.data.startswith("grad_view_"))
async def view_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """View ad"""
    logger.info(f"GRADUATE grad_view triggered: {callback.data} by {callback.from_user.id}")
    ad_id = int(callback.data.split("_")[2])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
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
    
    if ad[5]:  # file_id exists
        full_text += "\n📄 <b>Resume:</b> Yuklangan ✅"
    
    await callback.message.edit_text(
        full_text,
        reply_markup=ad_actions_keyboard_graduate(ad_id, ad[3], language),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith("edit_field_"), GraduateStates.edit)
async def select_edit_field(callback: CallbackQuery, state: FSMContext):
    """Select field to edit"""
    field_name = callback.data.split("edit_field_")[1]
    data = await state.get_data()
    language = data.get("language", "uz")
    
    await state.update_data(edit_field=field_name)
    
    if field_name == "region":
        await state.set_state(GraduateStates.edit_field)
        await callback.message.answer(
            get_text("enter_region", language),
            reply_markup=regions_keyboard(language)
        )
    elif field_name == "profession":
        await state.set_state(GraduateStates.edit_field)
        await callback.message.answer(
            get_text("enter_profession", language),
            reply_markup=categories_keyboard()
        )
    elif field_name == "contact":
        await state.set_state(GraduateStates.edit_field)
        from keyboards.base import contact_keyboard
        await callback.message.answer(
            get_text("enter_contact", language),
            reply_markup=contact_keyboard(language)
        )
    elif field_name == "resume":
        await state.set_state(GraduateStates.edit_field)
        await callback.message.answer(get_text("enter_resume", language))
    else:
        await state.set_state(GraduateStates.edit_field)
        
        field_texts = {
            "name": "enter_name",
            "age": "enter_age_gr",
            "technologies": "enter_technologies",
            "price": "enter_price",
            "contact_time": "enter_contact_time",
            "goal": "enter_goal"
        }
        
        text_key = field_texts.get(field_name, "enter_new_value")
        await callback.message.answer(get_text(text_key, language))
    
    await callback.message.delete()


@router.callback_query(F.data.startswith("region_"), GraduateStates.edit_field)
async def process_edit_region(callback: CallbackQuery, state: FSMContext):
    """Process edit region"""
    region_index = int(callback.data.split("_")[1])
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    regions = get_text("regions", language)
    new_value = regions[region_index]
    
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        old_value = ad_data.get("region", "")
        
        success = ad_service.update_ad_field(ad_id, "region", old_value, new_value, callback.from_user.id)
        
        if success:
            await callback.message.answer(get_text("field_updated", language))
            
            ad = ad_service.get_ad(ad_id)
            ad_data = json.loads(ad[4])
            ad_text = format_ad_text(ad_data, "graduate", language)
            
            await state.update_data(ad_id=ad_id)
            await state.set_state(GraduateStates.confirm)
            await callback.message.answer(
                f"{get_text('confirm_ad', language)}\n\n{ad_text}",
                reply_markup=confirmation_keyboard(language),
                parse_mode="HTML"
            )
    
    await callback.message.delete()


@router.callback_query(F.data.startswith("category_"), GraduateStates.edit_field)
async def process_edit_category(callback: CallbackQuery, state: FSMContext):
    """Process edit category"""
    category_id = int(callback.data.split("_")[1])
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    field_name = data.get("edit_field")
    
    categories = category_service.get_all_categories()
    new_value = next((name for id, name in categories if id == category_id), "")
    
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        old_value = ad_data.get(field_name, "")
        
        success = ad_service.update_ad_field(ad_id, field_name, old_value, new_value, callback.from_user.id)
        
        if success:
            await callback.message.answer(get_text("field_updated", language))
            
            ad = ad_service.get_ad(ad_id)
            ad_data = json.loads(ad[4])
            ad_text = format_ad_text(ad_data, "graduate", language)
            
            await state.update_data(ad_id=ad_id)
            await state.set_state(GraduateStates.confirm)
            await callback.message.answer(
                f"{get_text('confirm_ad', language)}\n\n{ad_text}",
                reply_markup=confirmation_keyboard(language),
                parse_mode="HTML"
            )
    
    await callback.message.delete()


@router.callback_query(F.data == "back_to_confirm", GraduateStates.edit)
async def back_to_confirm_from_edit(callback: CallbackQuery, state: FSMContext):
    """Back to confirm from edit"""
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "graduate", language)
        
        await state.set_state(GraduateStates.confirm)
        await callback.message.edit_text(
            f"{get_text('confirm_ad', language)}\n\n{ad_text}",
            reply_markup=confirmation_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "back_to_confirm", GraduateStates.edit_field)
async def back_to_confirm_from_edit_field(callback: CallbackQuery, state: FSMContext):
    """Back to confirm from edit field"""
    data = await state.get_data()
    language = data.get("language", "uz")
    ad_id = data.get("ad_id")
    
    ad = ad_service.get_ad(ad_id)
    if ad:
        ad_data = json.loads(ad[4])
        ad_text = format_ad_text(ad_data, "graduate", language)
        await state.set_state(GraduateStates.confirm)
        await callback.message.edit_text(
            f"{get_text('confirm_ad', language)}\n\n{ad_text}",
            reply_markup=confirmation_keyboard(language),
            parse_mode="HTML"
        )


@router.callback_query(F.data == "my_ads")
async def my_ads_callback(callback: CallbackQuery, state: FSMContext):
    """My ads callback"""
    language = user_service.get_user_language(callback.from_user.id)
    ads = ad_service.get_user_ads(callback.from_user.id)
    
    if not ads:
        await callback.message.edit_text(
            get_text("no_ads", language),
            reply_markup=graduate_main_menu(language)
        )
        return
    
    await callback.message.edit_text(
        get_text("ads_list", language),
        reply_markup=my_ads_keyboard(ads, language)
    )


@router.callback_query(F.data.startswith("grad_confirm_draft_"))
async def confirm_draft_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Confirm draft ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
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
    ad_service.update_ad_status(ad_id, "pending", callback.from_user.id)
    
    # Send to admin
    ad_data = json.loads(ad[4])
    ad_text = format_ad_text(ad_data, "graduate", language)
    
    if ad[5]:  # file_id exists
        await callback.bot.send_document(
            chat_id=RESUME_ADMIN_GROUP_ID,
            document=ad[5],
            caption=f"📝 Yangi bitiruvchi e'loni #{ad_id}\n\n{ad_text}",
            reply_markup=admin_moderation_keyboard(ad_id),
            parse_mode="HTML"
        )
    else:
        await callback.bot.send_message(
            chat_id=RESUME_ADMIN_GROUP_ID,
            text=f"📝 Yangi bitiruvchi e'loni #{ad_id}\n\n{ad_text}",
            reply_markup=admin_moderation_keyboard(ad_id),
            parse_mode="HTML"
        )
    
    await callback.message.edit_text(
        get_text("ad_created", language),
        reply_markup=graduate_main_menu(language)
    )


@router.callback_query(F.data.startswith("grad_cancel_pending_"))
async def cancel_pending_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Cancel pending ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
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
    
    ad_service.update_ad_status(ad_id, "cancelled", callback.from_user.id)
    
    await callback.message.edit_text(
        f"❌ E'lon #{ad_id} bekor qilindi!",
        reply_markup=graduate_main_menu(language)
    )


@router.callback_query(F.data.startswith("grad_edit_draft_"))
async def edit_draft_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Edit draft ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
    if not is_valid:
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    await state.update_data(ad_id=ad_id, language=language, role="graduate")
    await state.set_state(GraduateStates.edit)
    await callback.message.edit_text(
        get_text("select_edit_field", language),
        reply_markup=edit_fields_keyboard_graduate(language)
    )


@router.callback_query(F.data.startswith("grad_edit_pending_"))
async def edit_pending_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Edit pending ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
    if not is_valid:
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad = ad_service.get_ad(ad_id)
    
    if not ad or ad[1] != callback.from_user.id:
        await callback.answer("E'lon topilmadi!")
        return
    
    await state.update_data(ad_id=ad_id, language=language, role="graduate")
    await state.set_state(GraduateStates.edit)
    await callback.message.edit_text(
        get_text("select_edit_field", language),
        reply_markup=edit_fields_keyboard_graduate(language)
    )


@router.callback_query(F.data.startswith("grad_delete_"))
async def delete_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Delete ad"""
    ad_id = int(callback.data.split("_")[2])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
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
            InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"grad_confirm_delete_{ad_id}"),
            InlineKeyboardButton(text="❌ Yo'q", callback_data=f"grad_view_{ad_id}")
        ]
    ])
    
    await callback.message.edit_text(
        f"🗑 E'lonni o'chirish\n\n⚠️ Bu e'lon sizning ro'yxatingizdan o'chib ketadi.\n\nRostdan ham o'chirmoqchimisiz?",
        reply_markup=confirm_keyboard
    )


@router.callback_query(F.data.startswith("grad_confirm_delete_"))
async def confirm_delete_ad_graduate(callback: CallbackQuery, state: FSMContext):
    """Confirm delete ad"""
    ad_id = int(callback.data.split("_")[3])
    
    is_valid, language = user_service.check_user_role(callback.from_user.id, "graduate")
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


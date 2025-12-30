"""Admin callback handlers"""
import json
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.fsm.context import FSMContext

from states.admin_states import AdminStates
from config import MAIN_CHANNEL_USERNAME
from services.user_service import UserService
from utils.admin_helpers import is_admin
from services.ad_service import AdService
from services.category_service import CategoryService
from services.admin_service import AdminService
from utils.text_formatters import format_ad_text
from data.languages import get_text
from keyboards.admin_keyboards import (
    admin_panel_keyboard, category_actions_keyboard,
    admin_categories_keyboard, categories_list_keyboard
)
from keyboards.graduate_keyboards import graduate_main_menu
from keyboards.employer_keyboards import employer_main_menu

router = Router()
logger = logging.getLogger(__name__)

user_service = UserService()
ad_service = AdService()
category_service = CategoryService()
admin_service = AdminService()


@router.callback_query(F.data.startswith("approve_"))
async def approve_ad(callback: CallbackQuery):
    """Approve ad"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad_id = int(callback.data.split("_")[1])
    ad = ad_service.get_ad(ad_id)
    
    if not ad:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad[3] != "pending":
        await callback.answer("E'lon allaqachon ko'rib chiqilgan!")
        return
    
    # Update status to approved
    ad_service.update_ad_status(ad_id, "approved", callback.from_user.id)
    
    # Send to channel
    bot = callback.bot
    ad_data = json.loads(ad[4])
    ad_text = format_ad_text(ad_data, ad[2])
    
    try:
        if ad[2] == "graduate" and ad[5]:  # Has resume
            await bot.send_document(
                chat_id=MAIN_CHANNEL_USERNAME,
                document=ad[5],
                caption=ad_text,
                parse_mode="HTML"
            )
        else:
            await bot.send_message(
                chat_id=MAIN_CHANNEL_USERNAME,
                text=ad_text,
                parse_mode="HTML"
            )
    except Exception as e:
        await callback.answer(f"Kanalga yuborishda xatolik: {str(e)}")
        return
    
    # Notify user
    user = user_service.get_user(ad[1])
    if user:
        language = user[3] or "uz"
        success_text = get_text("ad_approved", language)
        
        try:
            if user[2] == "graduate":
                await bot.send_message(ad[1], success_text, reply_markup=graduate_main_menu(language))
            else:
                await bot.send_message(ad[1], success_text, reply_markup=employer_main_menu(language))
        except Exception:
            pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
    ])
    
    try:
        await callback.message.edit_text(
            f"✅ E'lon #{ad_id} tasdiqlandi va kanalga yuborildi!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        # Handle "message is not modified" error
        if "not modified" in str(e).lower():
            await callback.answer("✅ E'lon tasdiqlandi!")
        else:
            await callback.message.answer(
                f"✅ E'lon #{ad_id} tasdiqlandi va kanalga yuborildi!",
                reply_markup=keyboard
            )


@router.callback_query(F.data.startswith("reject_"))
async def reject_ad(callback: CallbackQuery):
    """Reject ad"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad_id = int(callback.data.split("_")[1])
    ad = ad_service.get_ad(ad_id)
    
    if not ad:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad[3] != "pending":
        await callback.answer("E'lon allaqachon ko'rib chiqilgan!")
        return
    
    # Update status to rejected
    ad_service.update_ad_status(ad_id, "rejected", callback.from_user.id)
    
    # Notify user
    bot = callback.bot
    user = user_service.get_user(ad[1])
    if user:
        language = user[3] or "uz"
        reject_text = get_text("ad_rejected", language)
        
        try:
            if user[2] == "graduate":
                await bot.send_message(ad[1], reject_text, reply_markup=graduate_main_menu(language))
            else:
                await bot.send_message(ad[1], reject_text, reply_markup=employer_main_menu(language))
        except Exception:
            pass
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
    ])
    
    try:
        await callback.message.edit_text(
            f"❌ E'lon #{ad_id} rad etildi!",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        # Handle "message is not modified" error
        if "not modified" in str(e).lower():
            await callback.answer("❌ E'lon rad etildi!")
        else:
            await callback.message.answer(f"❌ E'lon #{ad_id} rad etildi!", reply_markup=keyboard)


@router.callback_query(F.data == "manage_categories")
async def manage_categories(callback: CallbackQuery):
    """Manage categories"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    await callback.message.edit_text(
        "📂 Kategoriyalar boshqaruvi",
        reply_markup=admin_categories_keyboard()
    )


@router.callback_query(F.data == "list_categories")
async def list_categories(callback: CallbackQuery):
    """List categories"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    categories = category_service.get_all_categories()
    text = "📂 Kategoriyalar ro'yxati:\n\n"
    
    for i, (cat_id, cat_name) in enumerate(categories, 1):
        text += f"{i}. {cat_name}\n"
    
    text += f"\n📊 Jami: {len(categories)} ta kategoriya"
    
    await callback.message.edit_text(
        text,
        reply_markup=categories_list_keyboard()
    )


@router.callback_query(F.data == "add_category")
async def add_category_start(callback: CallbackQuery, state: FSMContext):
    """Start adding category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    await callback.message.edit_text(
        "➕ Yangi kategoriya nomini kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="manage_categories")]
        ])
    )
    await state.set_state(AdminStates.waiting_category_name)


@router.callback_query(F.data.startswith("edit_category_"))
async def edit_category(callback: CallbackQuery):
    """Edit category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    cat_id = int(callback.data.split("_")[2])
    categories = category_service.get_all_categories()
    category = next((cat for cat in categories if cat[0] == cat_id), None)
    
    if not category:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    await callback.message.edit_text(
        f"📂 Kategoriya: {category[1]}\n\nNima qilishni xohlaysiz?",
        reply_markup=category_actions_keyboard(cat_id)
    )


@router.callback_query(F.data.startswith("edit_cat_name_"))
async def edit_category_name(callback: CallbackQuery, state: FSMContext):
    """Edit category name"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    cat_id = int(callback.data.split("_")[3])
    categories = category_service.get_all_categories()
    category = next((cat for cat in categories if cat[0] == cat_id), None)
    
    if not category:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    await state.update_data(editing_category_id=cat_id)
    await callback.message.edit_text(
        f"✏️ Hozirgi nom: {category[1]}\n\nYangi nomni kiriting:",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data=f"edit_category_{cat_id}")]
        ])
    )
    await state.set_state(AdminStates.waiting_category_edit)


@router.callback_query(F.data.startswith("delete_cat_"))
async def delete_category_confirm(callback: CallbackQuery):
    """Confirm delete category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    cat_id = int(callback.data.split("_")[2])
    categories = category_service.get_all_categories()
    category = next((cat for cat in categories if cat[0] == cat_id), None)
    
    if not category:
        await callback.answer("Kategoriya topilmadi!")
        return
    
    await callback.message.edit_text(
        f"🗑 Kategoriyani o'chirish\n\n📂 {category[1]}\n\n⚠️ Bu amalni qaytarib bo'lmaydi!\nRostdan ham o'chirishni xohlaysizmi?",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Ha, o'chirish", callback_data=f"confirm_delete_{cat_id}"),
                InlineKeyboardButton(text="❌ Yo'q", callback_data=f"edit_category_{cat_id}")
            ]
        ])
    )


@router.callback_query(F.data.startswith("confirm_delete_"))
async def delete_category_final(callback: CallbackQuery):
    """Delete category"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    cat_id = int(callback.data.split("_")[2])
    
    success, error = category_service.delete_category(cat_id)
    if success:
        await callback.message.edit_text(
            f"✅ Kategoriya o'chirildi!",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="📂 Kategoriyalarga qaytish", callback_data="list_categories")]
            ])
        )
    else:
        await callback.answer(f"❌ Xatolik: {error}")


@router.callback_query(F.data == "stats")
async def show_stats(callback: CallbackQuery):
    """Show full statistics"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    stats = admin_service.get_full_statistics()
    user_stats = stats['users']
    ad_stats = stats['ads']
    
    # Calculate percentages
    total_users = user_stats['total']
    total_ads = ad_stats['total']
    
    user_percent_graduates = (user_stats['graduates'] / total_users * 100) if total_users > 0 else 0
    user_percent_employers = (user_stats['employers'] / total_users * 100) if total_users > 0 else 0
    
    ad_percent_approved = (ad_stats['approved'] / total_ads * 100) if total_ads > 0 else 0
    ad_percent_pending = (ad_stats['pending'] / total_ads * 100) if total_ads > 0 else 0
    
    text = (
        f"📊 <b>To'liq Statistika</b>\n\n"
        f"👥 <b>Foydalanuvchilar:</b>\n"
        f"   • Jami: {user_stats['total']}\n"
        f"   • Bitiruvchilar: {user_stats['graduates']} ({user_percent_graduates:.1f}%)\n"
        f"   • Ish beruvchilar: {user_stats['employers']} ({user_percent_employers:.1f}%)\n\n"
        f"📝 <b>E'lonlar:</b>\n"
        f"   • Jami: {ad_stats['total']}\n"
        f"   • ✅ Tasdiqlangan: {ad_stats['approved']} ({ad_percent_approved:.1f}%)\n"
        f"   • ⏳ Kutilayotgan: {ad_stats['pending']} ({ad_percent_pending:.1f}%)\n"
        f"   • ❌ Rad etilgan: {ad_stats['rejected']}\n"
        f"   • 🚫 Bekor qilingan: {ad_stats['cancelled']}"
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
    ])
    
    await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data == "pending_ads")
async def show_pending_ads(callback: CallbackQuery):
    """Show pending ads list"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ads_list = admin_service.get_pending_ads_list(limit=20)
    
    if not ads_list:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔙 Orqaga", callback_data="back_admin")]
        ])
        try:
            await callback.message.edit_text("⏳ Kutilayotgan e'lonlar yo'q!", reply_markup=keyboard)
        except Exception as e:
            if "not modified" in str(e).lower():
                await callback.answer("✅")
            else:
                await callback.message.answer("⏳ Kutilayotgan e'lonlar yo'q!", reply_markup=keyboard)
        return
    
    # Create keyboard with ad buttons
    from keyboards.admin_keyboards import pending_ads_list_keyboard
    keyboard = pending_ads_list_keyboard(ads_list)
    
    text = f"⏳ <b>Kutilayotgan e'lonlar ({len(ads_list)}):</b>\n\n"
    text += "E'lonni ko'rish uchun tanlang:"
    
    try:
        await callback.message.edit_text(text, reply_markup=keyboard, parse_mode="HTML")
    except Exception as e:
        # Handle "message is not modified" error
        if "not modified" in str(e).lower():
            await callback.answer("✅")
        else:
            await callback.message.answer(text, reply_markup=keyboard, parse_mode="HTML")


@router.callback_query(F.data.startswith("view_pending_ad_"))
async def view_pending_ad_details(callback: CallbackQuery):
    """View full details of pending ad"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    ad_id = int(callback.data.split("_")[3])
    ad = ad_service.get_ad(ad_id)
    
    if not ad:
        await callback.answer("E'lon topilmadi!")
        return
    
    if ad[3] != "pending":
        await callback.answer("Bu e'lon kutilayotgan holatda emas!")
        return
    
    # Get user language for formatting
    user = user_service.get_user(ad[1])
    language = user[3] if user else "uz"
    
    # Format full ad details
    full_text = admin_service.format_pending_ad_details(ad, language)
    
    # Add action buttons
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Tasdiqlash", callback_data=f"approve_{ad_id}"),
            InlineKeyboardButton(text="❌ Rad etish", callback_data=f"reject_{ad_id}")
        ],
        [
            InlineKeyboardButton(text="📋 Kutilayotganlar ro'yxati", callback_data="pending_ads"),
            InlineKeyboardButton(text="🏠 Admin panel", callback_data="back_admin")
        ]
    ])
    
    # Send document if exists, otherwise send message
    if ad[5]:  # file_id exists
        try:
            await callback.bot.send_document(
                chat_id=callback.from_user.id,
                document=ad[5],
                caption=full_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            await callback.message.delete()
        except Exception as e:
            # Handle "message is not modified" error
            if "not modified" in str(e).lower():
                await callback.answer("✅")
            else:
                try:
                    await callback.message.edit_text(
                        full_text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except Exception:
                    await callback.message.answer(
                        full_text,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
    else:
        try:
            await callback.message.edit_text(
                full_text,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            # Handle "message is not modified" error
            if "not modified" in str(e).lower():
                await callback.answer("✅")
            else:
                await callback.message.answer(
                    full_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )


@router.callback_query(F.data.in_(["back_admin", "back_to_admin_panel"]))
async def back_to_admin_panel(callback: CallbackQuery):
    """Back to admin panel - unified handler"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    try:
        await callback.message.edit_text(
            "🔧 Admin Panel",
            reply_markup=admin_panel_keyboard()
        )
    except Exception as e:
        # Handle "message is not modified" error
        if "not modified" in str(e).lower():
            await callback.answer("✅")
        else:
            # If edit fails, send new message
            await callback.message.answer(
                "🔧 Admin Panel",
                reply_markup=admin_panel_keyboard()
            )


@router.callback_query(F.data == "exit_admin")
async def exit_admin_panel(callback: CallbackQuery, state: FSMContext):
    """Exit admin panel and return to main menu - like /start command"""
    if not is_admin(callback.from_user.id):
        await callback.answer("Sizda ruxsat yo'q!")
        return
    
    # Clear state like /start does
    await state.clear()
    
    user = user_service.get_user(callback.from_user.id)
    if not user:
        try:
            await callback.message.edit_text(
                "🔧 Admin Panel",
                reply_markup=admin_panel_keyboard()
            )
        except Exception:
            await callback.message.answer(
                "🔧 Admin Panel",
                reply_markup=admin_panel_keyboard()
            )
        return
    
    language = user[3] or "uz"
    role = user[2]
    
    from keyboards.graduate_keyboards import graduate_main_menu
    from keyboards.employer_keyboards import employer_main_menu
    from keyboards.student_keyboards import student_main_menu
    
    # Use answer instead of edit_text to avoid "message is not modified" error
    # and delete old message like /start does
    try:
        if role == "graduate":
            await callback.message.answer(
                f"🎓 {get_text('graduate', language)} asosiy menyu",
                reply_markup=graduate_main_menu(language)
            )
        elif role == "employer":
            await callback.message.answer(
                f"👔 {get_text('employer', language)} asosiy menyu",
                reply_markup=employer_main_menu(language)
            )
        elif role == "student":
            await callback.message.answer(
                f"📚 {get_text('student', language)} asosiy menyu",
                reply_markup=student_main_menu(language)
            )
        else:
            await callback.message.answer(
                "🔧 Admin Panel",
                reply_markup=admin_panel_keyboard()
            )
        
        # Delete old message
        try:
            await callback.message.delete()
        except Exception:
            pass
    except Exception as e:
        logger.error(f"Exit admin panel error: {str(e)}")
        await callback.answer("Xatolik yuz berdi!")


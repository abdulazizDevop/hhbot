"""Text formatting utilities"""
import json
from datetime import datetime
from data.languages import get_text


def format_ad_text(ad_data: dict, ad_type: str, language: str = "uz") -> str:
    """Format ad text for display"""
    data = ad_data if isinstance(ad_data, dict) else json.loads(ad_data)
    
    if ad_type == "graduate":
        text = f"""
🎓 <b>Ustudy Bitiruvchisi</b>

👤 <b>Ism:</b> {data.get('name', 'Kiritilmagan')}
🎂 <b>Yosh:</b> {data.get('age', 'Kiritilmagan')}
💻 <b>Texnologiyalar:</b> {data.get('technologies', 'Kiritilmagan')}
📞 <b>Aloqa:</b> {data.get('contact', 'Kiritilmagan')}
🌍 <b>Hudud:</b> {data.get('region', 'Kiritilmagan')}
💰 <b>Narx:</b> {data.get('price', 'Kiritilmagan')}
💼 <b>Kasb:</b> {data.get('profession', 'Kiritilmagan')}
⏰ <b>Murojaat vaqti:</b> {data.get('contact_time', 'Kiritilmagan')}
🎯 <b>Maqsad:</b> {data.get('goal', 'Kiritilmagan')}
        """.strip()
    else:  # employer
        text = f"""
👔 <b>Ish E'loni</b>

🏢 <b>Ishxona:</b> {data.get('company', 'Kiritilmagan')}
👤 <b>Ism:</b> {data.get('name', 'Kiritilmagan')}
🎂 <b>Yosh:</b> {data.get('age', 'Kiritilmagan')}
📂 <b>Kategoriya:</b> {data.get('category', 'Kiritilmagan')}
👥 <b>Jins:</b> {data.get('gender', 'Kiritilmagan')}
📈 <b>Tajriba:</b> {data.get('experience', 'Kiritilmagan')}
📅 <b>Ish kunlari:</b> {data.get('work_days', 'Kiritilmagan')}
🕐 <b>Ish vaqti:</b> {data.get('work_hours', 'Kiritilmagan')}
📍 <b>Manzil:</b> {data.get('location', 'Kiritilmagan')}
💵 <b>Maosh:</b> {data.get('salary', 'Kiritilmagan')}
📝 <b>Talablar:</b> {data.get('requirements', 'Kiritilmagan')}
        """.strip()
    
    return text


def format_date(date_str: str) -> str:
    """Format date string"""
    try:
        dt = datetime.fromisoformat(date_str)
        return dt.strftime("%d.%m.%Y %H:%M")
    except Exception:
        return date_str


def get_status_text(status: str, language: str = "uz") -> str:
    """Get status text in specified language"""
    status_map = {
        'draft': get_text('ad_status_draft', language),
        'pending': get_text('ad_status_pending', language),
        'approved': get_text('ad_status_approved', language),
        'rejected': get_text('ad_status_rejected', language),
        'cancelled': get_text('ad_status_cancelled', language)
    }
    return status_map.get(status, status)


# languages.py
LANGUAGES = {
    "uz": "🇺🇿 O'zbek",
    "ru": "🇷🇺 Русский"
}

uz = {
    # Main texts
    "welcome": "Assalamu alaykum! Ustudy botidan foydalanish uchun tilni tanlang:",
    "select_role": "Siz kimsiz?",
    "graduate": "🎓 Ustudy bitiruvchisi",
    "employer": "👔 Ish beruvchi",
    "student": "📚 Ustudy o'quvchisi",
    
    # Menu buttons
    "create_ad": "E'lon yaratish",
    "my_ads": "Mening e'lonlarim",
    "create_ad_employer": "E'lon yaratish",
    "my_ads_employer": "Mening e'lonlarim",
    "contact_admin": "👨‍💼 Admin bilan bog'lanish",
    "browse_by_category": "Kategoriyalar bo'yicha ko'rish",
    
    # Graduate fields
    "enter_name": "Ism va familiyangizni kiriting:",
    "enter_age_gr": "Yoshingizni kiriting:",
    "enter_technologies": "Bilgan texnologiyalarni kiriting:\n(Texnologiya nomlarini vergul bilan ajrating. Masalan: Python, Django, PostgreSQL)",
    "enter_contact": "Bog'lanish uchun telefon raqamingizni kiriting:\n(Masalan: +998 90 123 45 67)",
    "enter_region": "Hududni tanlang:",
    "enter_price": "Qancha maoshga ishlamoqchisiz? (masalan: 500-1000$)",
    "enter_profession": "Qaysi yo'nalishda mutaxassislashasiz?",
    "enter_contact_time": "Qachon murojaat qilish mumkin?",
    "enter_goal": "Maqsadingizni kiriting:",
    "enter_resume": "Resume faylini yuklang:",
    
    # Employer fields
    "enter_age_emp": "Talab qilinadigan yoshni kiriting: (18-65)",
    "enter_company": "Kompaniya nomini kiriting:",
    "enter_job_category": "Ish kategoriyasini tanlang:",
    "enter_gender": "Kimlar uchun ish? (erkak, ayol, farqi yo'q)",
    "enter_experience": "Qancha tajriba talab qilinadi? (masalan: 1 yil, 6 oy):",
    "enter_work_days": "Ish kunlarini kiriting: (masalan: 5/2, 6/1)",
    "enter_work_hours": "Ish vaqtini kiriting: (masalan: 09:00-18:00)",
    "enter_location": "Ish joyining manzilini kiriting:",
    "enter_salary": "Maosh miqdorini kiriting: (masalan: 500-1000$)",
    "enter_requirements": "Qo'shimcha talablar (ixtiyoriy):",
    
    # Confirmation
    "confirm_ad": "Ma'lumotlaringizni tekshiring:",
    "confirm_btn": "✅ Tasdiqlash",
    "edit_btn": "✏️ Tahrirlash", 
    "cancel_btn": "❌ Bekor qilish",
    
    # Status messages
    "ad_created": "✅ E'lon muvaffaqiyatli yaratildi va admin tasdiqlashiga yuborildi!",
    "ad_cancelled": "❌ E'lon bekor qilindi!",
    "ad_approved": "🎉 Tabriklaymiz! Sizning e'loningiz tasdiqlandi va kanalda nashr qilindi!",
    "ad_rejected": "😔 Afsuski, sizning e'loningiz rad etildi. Iltimos, ma'lumotlarni to'g'rilab qaytadan urinib ko'ring.",
    
    # Edit
    "select_edit_field": "Qaysi ma'lumotni o'zgartirishni istaysiz?",
    "edit_name": "👤 Ism-familiya",
    "edit_age": "🎂 Yosh", 
    "edit_technologies": "💻 Texnologiyalar",
    "edit_contact": "📞 Telefon raqam",
    "edit_region": "🌍 Hudud",
    "edit_price": "💰 Maosh",
    "edit_profession": "💼 Mutaxassislik",
    "edit_contact_time": "⏰ Murojaat vaqti",
    "edit_goal": "🎯 Maqsad",
    "edit_company": "🏢 Kompaniya",
    "edit_category": "📂 Kategoriya",
    "edit_gender": "👥 Jins",
    "edit_experience": "📈 Tajriba",
    "edit_work_days": "📅 Ish kunlari",
    "edit_work_hours": "🕐 Ish vaqti",
    "edit_location": "📍 Manzil",
    "edit_salary": "💵 Maosh",
    "edit_requirements": "📝 Talablar",
    
    "enter_new_value": "Yangi qiymatni kiriting:",
    "field_updated": "Ma'lumot muvaffaqiyatli yangilandi! ✅",
    
    # My ads
    "no_ads": "Sizda hozircha birorta ham e'lon yo'q.",
    "ads_list": "Sizning barcha e'lonlaringiz:",
    "select_category": "📂 Kategoriyani tanlang",
    "no_ads_in_category": "Bu kategoriya uchun e'lon topilmadi: {category}",
    "category_results": "📂 Tanlangan kategoriya: {category}\nQuyidagi e'lonlar topildi:",
    "ad_status_draft": "📝 Qoralama",
    "ad_status_pending": "⏳ Ko'rib chiqilmoqda",
    "ad_status_approved": "✅ Tasdiqlangan",
    "ad_status_rejected": "❌ Rad etilgan",
    "ad_status_cancelled": "🚫 Bekor qilingan",
    
    # Regions
    "regions": [
        "Toshkent shahri", "Toshkent viloyati", "Qashqadaryo", "Samarqand",
        "Andijon", "Buxoro", "Jizzax", "Namangan", "Navoiy",
        "Sirdaryo", "Surxondaryo", "Qoraqalpog'iston"
    ],
    "max_ads_limit": "Siz maksimal 10 ta e'lon yarata olasiz!",
    
    # Buttons
    "share_contact": "📱 Raqamni yuborish",
    "back": "🔙 Orqaga",
    "main_menu": "🏠 Bosh sahifa"
    ,
    # Student flow
    "student_send": "Taklif/Shikoyat yuborish",
    "enter_student_name": "Ismingizni kiriting:",
    "enter_student_direction": "Qaysi yo'nalishda o'qiysiz?",
    "enter_student_group": "O'qiyotgan guruhingizning raqamini kiriting:\n(Misol: U12)",
    "enter_student_type": "Taklifmi yoki shikoyatmi? (taklif/shikoyat)",
    "enter_student_message": "Matnni yozib yuboring:",
    "student_review": "Ma'lumotlaringizni tekshiring:",
    "student_type_suggest": "Taklif",
    "student_type_complaint": "Shikoyat",
    "student_message_sent": "✅ Taklif/shikoyatingiz muvaffaqiyatli yuborildi va admin ko'rib chiqishiga yuborildi!",
    # Labels (emoji-siz)
    "label_name": "Ism-familiya",
    "label_direction": "Yo'nalish",
    "label_group": "Guruh raqami",
    "label_type": "Tur",
    "label_message": "Matn"
}

ru = {
    # Main texts
    "welcome": "Добро пожаловать! Выберите язык для работы с ботом Ustudy:",
    "select_role": "Выберите вашу роль:",
    "graduate": "🎓 Выпускник Ustudy",
    "employer": "👔 Работодатель",
    "student": "📚 Ученик Ustudy",
    
    # Menu buttons
    "create_ad": "Создать объявление",
    "my_ads": "Мои объявления",
    "create_ad_employer": "Создать объявление",
    "my_ads_employer": "Мои объявления",
    "contact_admin": "👨‍💼 Связаться с администратором",
    "browse_by_category": "Просмотр по категориям",
    "max_ads_limit": "Вы можете создать максимум 10 объявлений!",
    
    # Graduate fields
    "enter_name": "Введите ваши имя и фамилию:",
    "enter_age_gr": "Укажите ваш возраст:",
    "enter_technologies": "Перечислите технологии, которыми владеете:\n(Разделите названия запятыми. Например: Python, Django, PostgreSQL)",
    "enter_contact": "Введите номер телефона для связи:\n(Например: +998 90 123 45 67)",
    "enter_region": "Выберите регион:",
    "enter_price": "На какую зарплату рассчитываете? (например: 500-1000$)",
    "enter_profession": "В какой области специализируетесь?",
    "enter_contact_time": "В какое время с вами можно связаться?",
    "enter_goal": "Опишите вашу цель:",
    "enter_resume": "Загрузите файл резюме:",
    
    # Employer fields
    "enter_company": "Введите название компании:",
    "enter_age_emp": "Укажите требуемый возраст: (18-65)",
    "enter_job_category": "Выберите категорию вакансии:",
    "enter_gender": "Для кого предназначена работа? (мужчина, женщина, не важно)",
    "enter_experience": "Какой опыт работы требуется? (например: 1 год, 6 месяцев):",
    "enter_work_days": "Укажите рабочие дни: (например: 5/2, 6/1)",
    "enter_work_hours": "Укажите рабочее время: (например: 09:00-18:00)",
    "enter_location": "Введите адрес места работы:",
    "enter_salary": "Укажите размер зарплаты: (например: 500-1000$)",
    "enter_requirements": "Дополнительные требования (необязательно):",
    
    # Confirmation
    "confirm_ad": "Проверьте правильность ваших данных:",
    "confirm_btn": "✅ Подтвердить",
    "edit_btn": "✏️ Редактировать",
    "cancel_btn": "❌ Отменить",
    
    # Status messages
    "ad_created": "✅ Объявление успешно создано и отправлено на модерацию!",
    "ad_cancelled": "❌ Объявление отменено!",
    "ad_approved": "🎉 Поздравляем! Ваше объявление одобрено и опубликовано в канале!",
    "ad_rejected": "😔 К сожалению, ваше объявление было отклонено. Пожалуйста, исправьте данные и попробуйте снова.",
    
    # Edit
    "select_edit_field": "Какую информацию хотите изменить?",
    "edit_name": "👤 Имя и фамилия",
    "edit_age": "🎂 Возраст",
    "edit_technologies": "💻 Технологии",
    "edit_contact": "📞 Номер телефона",
    "edit_region": "🌍 Регион",
    "edit_price": "💰 Зарплата",
    "edit_profession": "💼 Специализация",
    "edit_contact_time": "⏰ Время для связи",
    "edit_goal": "🎯 Цель",
    "edit_resume": "📄 Resume",
    "edit_company": "🏢 Компания",
    "edit_category": "📂 Категория",
    "edit_gender": "👥 Пол",
    "edit_experience": "📈 Опыт работы",
    "edit_work_days": "📅 Рабочие дни",
    "edit_work_hours": "🕐 Рабочее время",
    "edit_location": "📍 Адрес",
    "edit_salary": "💵 Зарплата",
    "edit_requirements": "📝 Требования",
    
    "enter_new_value": "Введите новое значение:",
    "field_updated": "Информация успешно обновлена! ✅",
    
    # My ads
    "no_ads": "У вас пока нет ни одного объявления.",
    "ads_list": "Все ваши объявления:",
    "select_category": "📂 Выберите категорию",
    "no_ads_in_category": "Объявления не найдены для: {category}",
    "category_results": "📂 Выбрана категория: {category}\nНайденные объявления:",
    "ad_status_draft": "📝 Черновик",
    "ad_status_pending": "⏳ На рассмотрении",
    "ad_status_approved": "✅ Одобрено",
    "ad_status_rejected": "❌ Отклонено",
    "ad_status_cancelled": "🚫 Отменено",
    
    # Regions
    "regions": [
        "г. Ташкент", "Ташкентская область", "Кашкадарьинская область", "Самаркандская область",
        "Андижанская область", "Бухарская область", "Джизакская область", "Наманганская область", "Навоийская область",
        "Сырдарьинская область", "Сурхандарьинская область", "Республика Каракалпакстан"
    ],
    
    # Buttons
    "share_contact": "📱 Отправить номер",
    "back": "🔙 Назад",
    "main_menu": "🏠 Главная страница"
    ,
    # Student flow
    "student_send": "Отправить Предложение/Жалобу",
    "enter_student_name": "Введите ваше имя:",
    "enter_student_direction": "Ваше направление обучения:",
    "enter_student_group": "Введите номер вашей группы:\n(Например: U12)",
    "enter_student_type": "Предложение или жалоба? (предложение/жалоба)",
    "enter_student_message": "Напишите текст сообщения:",
    "student_review": "Проверьте ваши данные:",
    "student_type_suggest": "Предложение",
    "student_type_complaint": "Жалоба",
    "student_message_sent": "✅ Ваше предложение/жалоба успешно отправлено и отправлено на рассмотрение администратору!",
    # Labels (без эмодзи)
    "label_name": "Имя и фамилия",
    "label_direction": "Направление",
    "label_group": "Номер группы",
    "label_type": "Тип",
    "label_message": "Текст"
}

def get_text(key: str, language: str = "uz"):
    """Get text by key and language"""
    texts = uz if language == "uz" else ru
    return texts.get(key, key)
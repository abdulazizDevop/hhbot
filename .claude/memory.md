# InternBot - Ish va amaliyot Telegram boti

## Maqsad
Talabalar va ish izlovchilar uchun Telegram bot. CV qabul qilish, vakansiyalar boshqarish, ish beruvchi-talaba tutashtirish.

## Tech Stack
- **Language:** Python
- **Framework:** aiogram 3.23.0 (Telegram Bot API, async)
- **Database:** SQLite (database/)
- **Architecture:** Dispatcher pattern, async/await

## Arxitektura
```
main.py          — Entry point
handlers/        — start, admin, employer, graduate, student
database/        — SQLite operations
services/        — Business logic
keyboards/       — Telegram UI tugmalar
config.py        — Bot token, settings
```

## Muhim logika
- 5 ta handler: start, admin, employer, graduate, student
- CV fayllarini qabul qilish va saqlash
- Admin guruh orqali ijoba/rad qilish
- Background task: file cleanup (24 soat + 6 soat interval)
- DB: resumes, vacancies, users

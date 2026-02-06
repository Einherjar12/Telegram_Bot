# Задание 1. Чат-бот протестирован.

# Задание 2.
# Базовый каркас бота создан (bot.py, config.py, database.py).
# pip install telebot

# Задание 3.
# Регистрация бота через BotFather (название, описание, about, иконка),
# токен вставляется в config.py.

import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
from database import Database

bot = telebot.TeleBot(TOKEN)
db = Database()

# /start — приветствие
@bot.message_handler(commands=["start"])
def start_bot(message):
    bot.send_message(
        message.chat.id,
        "👋 **Привет!**\n\n"
        "📌 Я бот фитнес-клуба.\n\n"
        "**Команды:**\n"
        "/coaches — персональные тренеры\n"
        "/groups — групповые занятия\n"
        "/today — расписание на сегодня\n"
        "/week — расписание на неделю\n"
        "/about — информация о боте",
        parse_mode="Markdown"
    )

# /about — информация о боте
@bot.message_handler(commands=["about"])
def about_bot(message):
    bot.send_message(
        message.chat.id,
        "ℹ️ **О боте**\n\n"
        "Этот бот показывает:\n"
        "👨‍🏫 Тренеров\n"
        "🤸 Групповые занятия\n"
        "📅 Расписание на день и неделю\n\n"
        "💡 Используйте команды, чтобы узнать информацию.",
        parse_mode="Markdown"
    )

# /coaches — список тренеров с кнопками
@bot.message_handler(commands=["coaches"])
def coaches_list(message):
    coaches = db.get_coaches()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in coaches.keys():
        keyboard.add(KeyboardButton(name))
    bot.send_message(
        message.chat.id,
        "👨‍🏫 **Выберите тренера** (кнопкой или введите имя):",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# /groups — список групп с кнопками
@bot.message_handler(commands=["groups"])
def groups_list(message):
    groups = db.get_groups()
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    for name in groups.keys():
        keyboard.add(KeyboardButton(name))
    bot.send_message(
        message.chat.id,
        "🤸 **Выберите групповое занятие** (кнопкой или введите название):",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# /today — расписание на день
@bot.message_handler(commands=["today"])
def today_schedule(message):
    schedule = db.get_schedule("today")
    text = "📅 **Расписание на сегодня:**\n\n" + "\n".join(f"• {lesson}" for lesson in schedule)
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# /week — расписание на неделю
@bot.message_handler(commands=["week"])
def week_schedule(message):
    schedule = db.get_schedule("week")
    text = "🗓️ **Расписание на неделю:**\n\n" + "\n".join(f"• {lesson}" for lesson in schedule)
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

# Обработка выбора тренера или группы текстом
@bot.message_handler(content_types=["text"])
def handle_text(message):
    user_text = message.text.strip().lower()

    # Проверяем тренеров
    coaches = db.get_coaches()
    for name, info in coaches.items():
        if user_text == name.lower():
            bot.send_message(message.chat.id, f"👨‍🏫 **{name}** — {info}", parse_mode="Markdown")
            return

    # Проверяем группы
    groups = db.get_groups()
    for name, info in groups.items():
        if user_text == name.lower():
            bot.send_message(message.chat.id, f"🤸 **{name}** — {info}", parse_mode="Markdown")
            return

    # Если неизвестная команда/имя
    bot.send_message(
        message.chat.id,
        "❗ **Не понял сообщение** 😅\n"
        "Используйте команды:\n"
        "/coaches, /groups, /today, /week, /about",
        parse_mode="Markdown"
    )

# Запуск бота
print("✅ Бот запущен и готов к работе!")
bot.infinity_polling()


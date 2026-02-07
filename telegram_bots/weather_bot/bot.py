import telebot
from telebot import types
import random
import datetime
from config import TOKEN
from database import Database

bot = telebot.TeleBot(TOKEN)
db = Database()

CITIES = ["Москва", "СПБ", "Сочи"]
WEATHER_VARIANTS = ["☀️ Солнечно и тепло", "🌧 Дождливо", "🌥 Облачно", "❄️ Снег", "💨 Ветрено"]

def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(
        types.KeyboardButton("Москва"),
        types.KeyboardButton("СПБ"),
        types.KeyboardButton("Сочи"),
        types.KeyboardButton("⭐ Избранное"),
        types.KeyboardButton("📜 История")
    )
    return keyboard

def weather_keyboard(city):
    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🔄 Обновить", callback_data=f"refresh_{city}"),
        types.InlineKeyboardButton("⭐ Добавить в избранное", callback_data=f"fav_{city}")
    )
    return keyboard

def generate_weather(city):
    temperature = random.randint(-5, 30)
    condition = random.choice(WEATHER_VARIANTS)
    weather_data = {
        "city": city,
        "temperature": temperature,
        "weather": condition,
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    return weather_data

def format_weather_message(weather_data):
    return (
        f"🌤️ Погода в {weather_data['city']}:\n"
        f"🌡 Температура: {weather_data['temperature']}°C\n"
        f"🌦 Состояние: {weather_data['weather']}\n"
        f"🕒 Обновлено: {weather_data['timestamp']}"
    )

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(
        message.chat.id,
        "Привет! Я бот-погоды 🌤\nВыберите город или посмотрите избранное.",
        reply_markup=main_keyboard()
    )

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    text = message.text.strip()
    user_id = message.chat.id

    # ----------------- Выбор города -----------------
    if text in CITIES:
        weather = generate_weather(text)
        db.save_history(user_id, text, weather["weather"])
        bot.send_message(user_id, format_weather_message(weather), reply_markup=weather_keyboard(text))

    # ----------------- Избранный город -----------------
    elif text == "⭐ Избранное":
        fav = db.get_favourite_city(user_id)
        if fav:
            weather = generate_weather(fav)
            db.save_history(user_id, fav, weather["weather"])
            bot.send_message(user_id, format_weather_message(weather), reply_markup=weather_keyboard(fav))
        else:
            bot.send_message(user_id,
                             "⭐ В избранном пока нет городов. Добавьте город, нажав ⭐ на погоде.",
                             reply_markup=main_keyboard())

    # ----------------- История -----------------
    elif text == "📜 История":
        history = db.get_history(user_id)
        if history:
            msg = "📜 Последние запросы:\n\n"
            for i, (city, weather, timestamp) in enumerate(history, 1):
                msg += f"{i}. {city} - {weather} | {timestamp}\n"
            bot.send_message(user_id, msg, reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "📜 История запросов пока пуста.", reply_markup=main_keyboard())

    else:
        bot.send_message(user_id, "Пожалуйста, выберите кнопку из меню ⬇️", reply_markup=main_keyboard())

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.from_user.id

    if call.data.startswith("refresh_"):
        city = call.data[8:]
        weather = generate_weather(city)
        db.save_history(user_id, city, weather["weather"])
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=format_weather_message(weather),
                              reply_markup=weather_keyboard(city))
        bot.answer_callback_query(call.id, "✅ Прогноз обновлён!")

    elif call.data.startswith("fav_"):
        city = call.data[4:]
        db.set_favourite_city(user_id, city)
        bot.answer_callback_query(call.id, f"⭐ {city} добавлен в избранное!")

if __name__ == '__main__':
    print("Бот запущен...")
    bot.infinity_polling()







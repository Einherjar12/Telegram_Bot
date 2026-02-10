import telebot
import requests
from telebot import types
from config import TOKEN, RANDOM_API_KEY
from database import init_db, save_value, get_user_data

bot = telebot.TeleBot(TOKEN)
init_db()

user_steps = {}      # состояние для генерации чисел
user_game = {}       # состояние для Орел/Решка
dice_game = {}       # состояние для игры с кубиками


# ---------- Функция генерации случайных чисел ----------
def get_random_numbers(range_start, range_end, amount):
    if range_start >= range_end:
        raise ValueError("Начало диапазона должно быть меньше конца диапазона.")
    if amount <= 0:
        raise ValueError("Количество чисел должно быть больше 0.")

    url = "https://api.random.org/json-rpc/4/invoke"
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": RANDOM_API_KEY,
            "n": amount,
            "min": range_start,
            "max": range_end,
            "replacement": True
        },
        "id": 1
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if "error" in data:
        raise ValueError(f"Ошибка random.org: {data['error']['message']}")
    return data["result"]["random"]["data"]


# ---------- Функция "Орел или Решка" ----------
def coin_flip():
    url = "https://api.random.org/json-rpc/4/invoke"
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": RANDOM_API_KEY,
            "n": 1,
            "min": 0,
            "max": 1,
            "replacement": True
        },
        "id": 1
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if "error" in data:
        raise ValueError(f"Ошибка random.org: {data['error']['message']}")
    return "Орел" if data["result"]["random"]["data"][0] == 0 else "Решка"


# ---------- Функция броска кубиков ----------
def roll_dice(n):
    if n <= 0:
        raise ValueError("Количество кубиков должно быть больше 0.")
    url = "https://api.random.org/json-rpc/4/invoke"
    payload = {
        "jsonrpc": "2.0",
        "method": "generateIntegers",
        "params": {
            "apiKey": RANDOM_API_KEY,
            "n": n,
            "min": 1,
            "max": 6,
            "replacement": True
        },
        "id": 1
    }
    response = requests.post(url, json=payload)
    data = response.json()
    if "error" in data:
        raise ValueError(f"Ошибка random.org: {data['error']['message']}")
    return data["result"]["random"]["data"]


# ---------- Главные кнопки ----------
def main_menu(chat_id, text="Выбери действие:"):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        types.KeyboardButton("Сгенерировать число"),
        types.KeyboardButton("Орел или Решка"),
        types.KeyboardButton("Игральные кости")
    )
    bot.send_message(chat_id, text, reply_markup=markup)


# ---------- Команда /start ----------
@bot.message_handler(commands=["start"])
def start_command(message):
    chat_id = message.chat.id
    welcome_text = (
        "Привет! 👋\n"
        "Я многофункциональный бот для случайных игр и генерации чисел.\n\n"
        "Вот что я умею:\n"
        "🎲 Сгенерировать случайные числа в указанном диапазоне\n"
        "🪙 Орел или Решка — проверь свою удачу\n"
        "🎲 Игральные кости — брось кубики и победи бота\n"
    )
    main_menu(chat_id, welcome_text)


# ---------- Кнопки для выбора игры ----------
@bot.message_handler(func=lambda message: message.text == "Сгенерировать число")
def generate_number_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Введи начало диапазона:")
    user_steps[chat_id] = "range_start"


@bot.message_handler(func=lambda message: message.text == "Орел или Решка")
def coin_game_button(message):
    chat_id = message.chat.id
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(types.KeyboardButton("Орел"), types.KeyboardButton("Решка"))
    bot.send_message(chat_id, "Выбери Орел или Решка:", reply_markup=markup)
    user_game[chat_id] = "await_choice"


@bot.message_handler(func=lambda message: message.text == "Игральные кости")
def dice_game_button(message):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Сколько кубиков бросить? (1-6)")
    dice_game[chat_id] = "await_count"


# ---------- Обработка всех сообщений ----------
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    step = user_steps.get(chat_id)
    game_step = user_game.get(chat_id)
    dice_step = dice_game.get(chat_id)

    # ---------- Орел или Решка ----------
    if game_step == "await_choice":
        if message.text not in ["Орел", "Решка"]:
            bot.send_message(chat_id, "Пожалуйста, выбери Орел или Решка.")
            return
        try:
            result = coin_flip()
        except ValueError as e:
            bot.send_message(chat_id, f"❌ Ошибка: {e}")
            return
        if message.text == result:
            bot.send_message(chat_id, f"🎉 Выпало: {result}. Ты выиграл!")
        else:
            bot.send_message(chat_id, f"😞 Выпало: {result}. Ты проиграл!")
        user_game.pop(chat_id)
        main_menu(chat_id)
        return

    # ---------- Игральные кости ----------
    if dice_step == "await_count":
        if not message.text.isdigit() or not (1 <= int(message.text) <= 6):
            bot.send_message(chat_id, "Введите число от 1 до 6.")
            return
        n = int(message.text)
        try:
            user_rolls = roll_dice(n)
            bot_rolls = roll_dice(n)
        except ValueError as e:
            bot.send_message(chat_id, f"❌ Ошибка: {e}")
            return

        user_sum = sum(user_rolls)
        bot_sum = sum(bot_rolls)

        text = (
            f"Твои кубики: {user_rolls} → сумма: {user_sum}\n"
            f"Кубики бота: {bot_rolls} → сумма: {bot_sum}\n"
        )
        if user_sum > bot_sum:
            text += "🎉 Ты победил!"
        elif user_sum < bot_sum:
            text += "😞 Бот победил!"
        else:
            text += "🤝 Ничья!"
        bot.send_message(chat_id, text)
        dice_game.pop(chat_id)
        main_menu(chat_id)
        return

    # ---------- Генерация чисел ----------
    if step:
        if not message.text.isdigit():
            bot.send_message(chat_id, "Пожалуйста, введи целое число 🔢")
            return
        value = int(message.text)

        if step == "range_start":
            save_value(chat_id, "range_start", value)
            bot.send_message(chat_id, "Теперь введи конец диапазона:")
            user_steps[chat_id] = "range_end"

        elif step == "range_end":
            save_value(chat_id, "range_end", value)
            bot.send_message(chat_id, "Сколько чисел нужно сгенерировать?")
            user_steps[chat_id] = "amount"

        elif step == "amount":
            save_value(chat_id, "amount", value)
            range_start, range_end, amount = get_user_data(chat_id)
            try:
                numbers = get_random_numbers(range_start, range_end, amount)
                bot.send_message(chat_id, f"🎲 Случайные числа:\n{numbers}")
            except ValueError as e:
                bot.send_message(chat_id, f"❌ Ошибка: {e}")
                bot.send_message(chat_id, "Попробуй ещё раз с правильными числами.")
                user_steps[chat_id] = "range_start"
                return
            user_steps.pop(chat_id)
            main_menu(chat_id)
        return


bot.polling(none_stop=True)





import telebot
import random
from telebot import types

import database
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
database.create_table()


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("🎲 Число", "🪙 Монетка", "🤔 Выбрать")
    return keyboard


@bot.message_handler(commands=["start"])
def start(message):
    text = (
        "Я бот-рандом 🎲\n\n"
        "Что я умею:\n"
        "🎲 Выдаю случайное число от 1 до 100\n"
        "🪙 Подбрасываю монетку (орёл или решка)\n"
        "🤔 Делаю случайный выбор\n\n"
        "Выбери действие кнопками ниже 👇"
    )

    bot.send_message(
        message.chat.id,
        text,
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "🎲 Число")
def random_number(message):
    number = random.randint(1, 100)
    database.inc_number(message.from_user.id)
    bot.send_message(message.chat.id, f"Случайное число: {number}")


@bot.message_handler(func=lambda m: m.text == "🪙 Монетка")
def coin(message):
    result = random.choice(["Орёл", "Решка"])
    database.inc_coin(message.from_user.id)
    bot.send_message(message.chat.id, result)


@bot.message_handler(func=lambda m: m.text == "🤔 Выбрать")
def choose(message):
    result = random.choice(["Да", "Нет"])
    bot.send_message(message.chat.id, result)


bot.polling()

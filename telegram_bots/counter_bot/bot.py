import telebot
from telebot import types

import database
from config import TOKEN

bot = telebot.TeleBot(TOKEN)
database.create_table()


def main_keyboard():
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add("+1", "Сбросить")
    return keyboard


@bot.message_handler(commands=["start"])
def start(message):
    bot.send_message(
        message.chat.id,
        "Это бот-счётчик 👋\nНажимай кнопки!",
        reply_markup=main_keyboard()
    )


@bot.message_handler(func=lambda m: m.text == "+1")
def plus_one(message):
    database.increment_count(message.from_user.id)
    count = database.get_count(message.from_user.id)
    bot.send_message(message.chat.id, f"Текущее значение: {count}")


@bot.message_handler(func=lambda m: m.text == "Сбросить")
def reset(message):
    database.reset_count(message.from_user.id)
    bot.send_message(message.chat.id, "Счётчик сброшен 🔄")


bot.polling()

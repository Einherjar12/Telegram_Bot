import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from config import TOKEN
from database import Database

bot = telebot.TeleBot(TOKEN)
db = Database()

quiz = [
    {"question": "Человек использует только 10% своего мозга?", "answer": "Нет",
     "explanation": "Это миф. Человек использует все части мозга, просто в разное время."},
    {"question": "Свет распространяется быстрее звука?", "answer": "Да",
     "explanation": "Свет распространяется со скоростью ~300 000 км/с, звук только ~343 м/с в воздухе."},
    {"question": "Земля находится ближе к Солнцу, чем Венера?", "answer": "Нет",
     "explanation": "Венера ближе к Солнцу, чем Земля."},
    {"question": "В клетке человека есть митохондрии?", "answer": "Да",
     "explanation": "Митохондрии — 'энергетические станции' клетки, они есть в каждой клетке человека."},
    {"question": "Атом водорода имеет два протона?", "answer": "Нет",
     "explanation": "Атом водорода имеет один протон."},
    {"question": "Шекспир написал пьесу 'Гамлет'?", "answer": "Да",
     "explanation": "'Гамлет' — одна из самых известных трагедий Уильяма Шекспира."},
    {"question": "Существуют только три состояния вещества?", "answer": "Нет",
     "explanation": "Помимо твердого, жидкого и газообразного, есть плазма, конденсат Бозе-Эйнштейна и др."},
    {"question": "Морская вода солёнее пресной?", "answer": "Да",
     "explanation": "Содержание соли в морской воде около 3,5%, а в пресной — меньше 0,1%."},
    {"question": "Чёрные дыры излучают энергию?", "answer": "Да",
     "explanation": "Это явление называется излучением Хокинга."},
    {"question": "Сатурн — это самая большая планета Солнечной системы?", "answer": "Нет",
     "explanation": "Самая большая планета — Юпитер."}
]

# Хранение текущего вопроса для каждого пользователя
user_state = {}

# Клавиатура Да/Нет
yes_no_keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
yes_no_keyboard.add(KeyboardButton("Да"), KeyboardButton("Нет"))


# /start
@bot.message_handler(commands=["start"])
def start_quiz(message):
    user_id = message.from_user.id
    db.add_user_if_not_exists(user_id)
    user_state[user_id] = 0  # первый вопрос
    bot.send_message(
        user_id,
        "Привет! Это викторина 'Да/Нет' 🎯\n"
        "Отвечай на вопросы, выбирая кнопки 'Да' или 'Нет'.\n"
        "Начнём!",
        reply_markup=yes_no_keyboard
    )
    send_question(user_id)


# Функция отправки вопроса
def send_question(user_id):
    idx = user_state.get(user_id, 0)
    if idx < len(quiz):
        question_text = quiz[idx]["question"]
        bot.send_message(user_id, f"Вопрос {idx + 1}: {question_text}", reply_markup=yes_no_keyboard)
    else:
        correct, total = db.get_result(user_id)
        bot.send_message(user_id,
                         f"🎉 Викторина завершена!\n"
                         f"Ваш результат: {correct}/{total} правильных ответов.")
        user_state[user_id] = 0  # сброс на начало


# Обработка ответов Да/Нет
@bot.message_handler(content_types=["text"])
def handle_answer(message):
    user_id = message.from_user.id
    idx = user_state.get(user_id, 0)

    if idx >= len(quiz):
        bot.send_message(user_id, "Викторина уже завершена. Напиши /start для повторного прохождения.")
        return

    user_answer = message.text.strip()
    correct_answer = quiz[idx]["answer"]
    explanation = quiz[idx]["explanation"]

    if user_answer not in ["Да", "Нет"]:
        bot.send_message(user_id, "Пожалуйста, отвечай только 'Да' или 'Нет'.")
        return

    if user_answer == correct_answer:
        db.update_result(user_id, correct_increment=1)
        bot.send_message(user_id, f"✅ Правильно!\n💡 {explanation}")
    else:
        db.update_result(user_id)
        bot.send_message(user_id, f"❌ Неправильно!\nПравильный ответ: {correct_answer}\n💡 {explanation}")

    # Переход к следующему вопросу
    user_state[user_id] = idx + 1
    send_question(user_id)


bot.infinity_polling()

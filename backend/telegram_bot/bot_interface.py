import telebot.types


def get_start_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создаем кнопки в два столбца
    markup.row(
        telebot.types.KeyboardButton("📝 Начать игру"),
        telebot.types.KeyboardButton("🎁 Проверить монеты"),
    )
    markup.row(
        telebot.types.KeyboardButton("🎫 Обмен монет"),
        telebot.types.KeyboardButton("🔍 Смотреть неправильные ответы"),
    )

    return markup


def get_questions_management_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        telebot.types.KeyboardButton("➕ Добавить вопрос"),
        telebot.types.KeyboardButton("🗑 Удалить вопрос"),
    )
    markup.row(
        telebot.types.KeyboardButton("📋 Список вопросов"),
        telebot.types.KeyboardButton("🏠 Вернуться в меню"),
    )
    return markup


def get_promo_management_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        telebot.types.KeyboardButton("➕ Добавить промокод"),
        telebot.types.KeyboardButton("🗑 Удалить промокод"),
    )
    markup.row(
        telebot.types.KeyboardButton("📋 Список промокодов"),
        telebot.types.KeyboardButton("🏠 Вернуться в меню"),
    )
    return markup


def get_bonus_exchange_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        telebot.types.KeyboardButton("🎫 5%"),
        telebot.types.KeyboardButton("🎫 10%"),
    )
    markup.row(telebot.types.KeyboardButton("🏠 Вернуться в меню"))
    return markup


def get_quiz_finish_markup():
    markup = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.row(
        telebot.types.KeyboardButton("🏠 Вернуться в меню"),
        telebot.types.KeyboardButton("🔍 Смотреть неправильные ответы"),
    )
    return markup


def get_answer_markup(options, q_id, chat_id):
    markup = telebot.types.InlineKeyboardMarkup(row_width=1)
    for i, option in enumerate(options):
        markup.add(
            telebot.types.InlineKeyboardButton(
                option, callback_data=f"a|{q_id}|{chat_id}|{i}"
            )
        )

    return markup

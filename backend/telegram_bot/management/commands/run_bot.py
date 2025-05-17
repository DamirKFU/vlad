import random
import string

import django.conf
import django.core.management.base
import django.core.signing
import django.db.models

import telegram_bot.bot
import telegram_bot.bot_interface
import telegram_bot.models
import users.models

user_sessions = {}


def get_user_from_message(message):
    user = users.models.User.objects.filter(
        telegram_id=message.from_user.id
    ).first()
    if user is None:
        auth_url = "{}/api/telegram-bot/auth?token={}".format(
            django.conf.settings.SITE_URL,
            django.core.signing.dumps(message.chat.id),
        )
        telegram_bot.bot.bot.reply_to(
            message,
            "Привет! Для связки аккаунта перейдите по ссылке:\n{}".format(
                auth_url
            ),
        )

    return user


def get_user_from_callback(call):
    return users.models.User.objects.filter(
        telegram_id=call.from_user.id
    ).first()


def convert_values_to_list(values):
    return [tuple(x.values()) for x in list(values)]


def send_next_question(chat_id, user):
    session = user_sessions.get(chat_id)
    if not session or not session["questions"]:
        finish_quiz(chat_id)
        return

    question_data = session["questions"][0]
    q_id, question, correct, wrong1, wrong2, wrong3 = question_data
    options = [correct, wrong1, wrong2, wrong3]
    random.shuffle(options)

    # Сохраняем перемешанные варианты в сессии
    session["current_options"] = options

    markup = telegram_bot.bot_interface.get_answer_markup(
        options, q_id, chat_id
    )
    telegram_bot.bot.bot.send_message(
        chat_id, f"❓ {question}", reply_markup=markup
    )


def finish_quiz(chat_id, user):
    session = user_sessions.get(chat_id)
    if not session:
        return

    correct = session["correct_count"]
    wrong = session["wrong_count"]
    total = correct + wrong
    bonus = int(correct)

    user.bonus = django.db.models.F(users.models.User.bonus.field.name) + bonus

    user.save(update_fields=[users.models.User.bonus.field.name])

    result_message = (
        f"🏁 Викторина завершена!\n\n"
        f"✅ Правильных ответов: {correct}\n"
        f"❌ Неправильных ответов: {wrong}\n"
        f"📊 Всего вопросов: {total}\n"
        f"🎁 Вы заработали: {bonus} монет"
    )

    markup = telegram_bot.bot_interface.get_quiz_finish_markup()
    telegram_bot.bot.bot.send_message(
        chat_id, result_message, reply_markup=markup
    )
    user_sessions.pop(chat_id, None)


class Command(django.core.management.base.BaseCommand):

    def handle(self, *args, **options):
        @telegram_bot.bot.bot.message_handler(commands=["start"])
        def send_welcome(message):
            if get_user_from_message(message) is None:
                return

            markup = telegram_bot.bot_interface.get_start_markup()
            telegram_bot.bot.bot.send_message(
                message.chat.id,
                "Привет! Я бот-викторина. Выберите одну из опций:",
                reply_markup=markup,
            )

        @telegram_bot.bot.bot.message_handler(
            func=lambda message: message.text == "📝 Начать игру"
        )
        def start_quiz(message):
            user = get_user_from_message(message)
            if user is None:
                return

            telegram_bot.models.WrongAnswer.objects.filter(user=user).delete()
            questions = convert_values_to_list(
                telegram_bot.models.Question.objects.all().values()
            )

            if not questions:
                telegram_bot.bot.bot.send_message(
                    message.chat.id,
                    (
                        "❌ В базе нет вопросов. Попросите администратора"
                        " добавить вопросы",
                    ),
                )
                return

            random.shuffle(questions)
            user_sessions[message.chat.id] = {
                "questions": questions,
                "correct_count": 0,
                "wrong_count": 0,
                "current_options": None,
            }

            send_next_question(message.chat.id, user)

        @telegram_bot.bot.bot.callback_query_handler(
            func=lambda call: call.data.startswith("a|")
        )
        def check_answer(call):
            parts = call.data.split("|")
            q_id = int(parts[1])
            chat_id = int(parts[2])
            answer_index = int(parts[3])
            user = get_user_from_callback(call)

            session = user_sessions.get(chat_id)
            if not session:
                return

            question_data = session["questions"][0]
            correct_answer = question_data[2]

            # Получаем ответ пользователя из сохраненных перемешанных вариантов
            user_answer = session["current_options"][answer_index]

            if user_answer.strip() == correct_answer.strip():
                session["correct_count"] += 1
            else:
                session["wrong_count"] += 1
                telegram_bot.models.WrongAnswer(
                    user=user,
                    question=question_data[1],
                    user_answer=user_answer,
                    correct_answer=correct_answer,
                ).save()

            session["questions"].pop(0)
            session.pop("current_options", None)

            if not session["questions"]:
                telegram_bot.bot.bot.delete_message(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                )
                finish_quiz(chat_id, user)
            else:
                # Получаем следующий вопрос и его варианты ответов
                question_data = session["questions"][0]
                q_id, question, correct, wrong1, wrong2, wrong3 = question_data
                options = [correct, wrong1, wrong2, wrong3]
                random.shuffle(options)

                # Сохраняем новые перемешанные варианты
                session["current_options"] = options

                markup = telegram_bot.bot_interface.get_answer_markup(
                    options, q_id, chat_id
                )

                telegram_bot.bot.bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=f"❓ {question}",
                    reply_markup=markup,
                )

        @telegram_bot.bot.bot.message_handler(
            func=lambda message: message.text
            == "🔍 Смотреть неправильные ответы"
        )
        def view_wrong_answers(message):
            wrong_answers = convert_values_to_list(
                telegram_bot.models.WrongAnswer.objects.all().values(
                    "question", "user_answer", "correct_answer"
                )
            )

            if not wrong_answers:
                telegram_bot.bot.bot.send_message(
                    message.chat.id, "❌ У вас нет неправильных ответов."
                )
                return

            wrong_answers_message = "❌ Неправильные ответы:\n\n"
            for question, user_answer, correct_answer in wrong_answers:
                wrong_answers_message += (
                    f"Вопрос: {question}\nВаш ответ: {user_answer}\n"
                )
                wrong_answers_message += (
                    f"Правильный ответ: {correct_answer}\n\n"
                )

            markup = telegram_bot.bot_interface.get_start_markup(
                message.chat.id in django.conf.settings.ADMIN_TELEGRAM_ID
            )
            telegram_bot.bot.bot.send_message(
                message.chat.id, wrong_answers_message, reply_markup=markup
            )

        @telegram_bot.bot.bot.message_handler(
            func=lambda message: message.text == "🎁 Проверить монеты"
        )
        def check_bonus(message):
            user = get_user_from_message(message)
            if user is None:
                return

            telegram_bot.bot.bot.send_message(
                message.chat.id, f"🎁 Ваш баланс: {user.bonus} монет"
            )

        @telegram_bot.bot.bot.message_handler(
            func=lambda message: message.text == "🎫 Обмен монет"
        )
        def exchange_bonus(message):
            user = get_user_from_message(message)
            if user is None:
                return

            current_bonus = user.bonus

            if current_bonus < min(django.conf.settings.PROMO_COSTS.values()):
                min_cost = min(django.conf.settings.PROMO_COSTS.values())
                telegram_bot.bot.bot.send_message(
                    message.chat.id,
                    (
                        f"❌ У вас недостаточно монет для обмена. "
                        f"Минимум {min_cost} монет.",
                    ),
                )
                return

            # Показываем доступные варианты обмена
            available_options = []
            options_text = "💫 Доступные варианты обмена:\n\n"

            for discount, cost in django.conf.settings.PROMO_COSTS.items():
                if current_bonus >= cost:
                    available_options.append(discount)
                    options_text += f"🎫 {discount}% скидка - {cost} монет\n"

            options_text += (
                f"\n💰 У вас есть: {current_bonus} монет"
                f"\nВыберите процент скидки:"
            )

            markup = telegram_bot.bot_interface.get_bonus_exchange_markup()
            telegram_bot.bot.bot.send_message(
                message.chat.id, options_text, reply_markup=markup
            )

        @telegram_bot.bot.bot.message_handler(
            func=lambda message: message.text in ["🎫 5%", "🎫 10%"]
        )
        def process_exchange(message):
            user = get_user_from_message(message)
            if user is None:
                return

            discount = int(message.text.strip("🎫 %"))
            required_bonus = int(django.conf.settings.PROMO_COSTS[discount])

            current_bonus = user.bonus

            if current_bonus < required_bonus:
                telegram_bot.bot.bot.send_message(
                    message.chat.id,
                    (
                        f"❌ У вас недостаточно монет. Для получения "
                        f"{discount}% скидки нужно {required_bonus} монет.",
                    ),
                )
                return

                # Генерируем промокод
            promo_code = "".join(
                random.choices(string.ascii_uppercase + string.digits, k=8)
            )

            # Сохраняем промокод в базе данных
            telegram_bot.models.PromoCode(
                promo_code=promo_code,
                discount=discount,
            ).save()

            # Вычитаем бонусы (используем целочисленные значения)
            new_bonus = current_bonus - required_bonus
            user.bonus = new_bonus
            user.save(update_fields=[users.models.User.bonus.field.name])

            telegram_bot.bot.bot.send_message(
                message.chat.id,
                f"🎉 Поздравляем! Ваш промокод на {discount}%: `{promo_code}`\n"
                f"\n🎁 Списано монет: {required_bonus}\n"
                f"💰 Осталось монет: {new_bonus}",
            )

            # Возвращаемся в главное меню
            send_welcome(message)

        self.stdout.write("Bot started")
        telegram_bot.bot.bot.infinity_polling()

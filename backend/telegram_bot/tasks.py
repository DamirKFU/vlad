import celery

import telegram_bot.bot


@celery.shared_task
def send_message(chat_id, message):
    telegram_bot.bot.bot.send_message(chat_id, message)

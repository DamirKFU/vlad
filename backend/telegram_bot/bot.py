import django.conf
import telebot

import telegram_bot.tasks

bot = telebot.TeleBot(django.conf.settings.TELEGRAM_BOT_TOKEN)


def send_order_status_update(chat_id, order_id, new_status):
    status_messages = {
        "PD": "Заказ в разрботке",
        "IW": "Заказ в работе",
        "DR": "Заказ готов",
        "ID": "Заказ в доставке",
        "DV": "Заказ доставлен",
    }

    message = "Статус заказа #{} изменен: {}".format(
        order_id,
        status_messages.get(new_status, new_status),
    )
    telegram_bot.tasks.send_message.delay(chat_id, message)

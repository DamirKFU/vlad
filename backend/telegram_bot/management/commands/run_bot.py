import django.conf
import django.core.management.base
import django.core.signing

import telegram_bot.bot


class Command(django.core.management.base.BaseCommand):

    def handle(self, *args, **options):
        @telegram_bot.bot.bot.message_handler(commands=["start"])
        def send_welcome(message):
            auth_url = "{}/telegram-auth?token={}".format(
                django.conf.settings.SITE_URL,
                django.core.signing.dumps(message.chat.id),
            )
            telegram_bot.bot.bot.reply_to(
                message,
                "Привет! Для связки аккаунта перейдите по ссылке:\n{}".format(
                    auth_url
                ),
            )

        self.stdout.write("Bot started")
        telegram_bot.bot.bot.infinity_polling()

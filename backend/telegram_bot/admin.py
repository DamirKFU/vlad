import django.contrib.admin

import telegram_bot.models


@django.contrib.admin.register(telegram_bot.models.Question)
class QuestionAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(telegram_bot.models.WrongAnswer)
class WrongAnswerAdmin(django.contrib.admin.ModelAdmin):
    pass


@django.contrib.admin.register(telegram_bot.models.PromoCode)
class PromoCodeAdmin(django.contrib.admin.ModelAdmin):
    pass

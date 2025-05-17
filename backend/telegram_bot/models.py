import django.db.models

import users.models


class Question(django.db.models.Model):
    question = django.db.models.TextField(
        verbose_name="Вопрос", help_text="Текст вопроса"
    )
    correct_answer = django.db.models.TextField(
        verbose_name="Правильный ответ", help_text="Правильный ответ на вопрос"
    )
    wrong_answer1 = django.db.models.TextField(
        verbose_name="Неправильный ответ 1",
        help_text="Первый неправильный ответ",
    )
    wrong_answer2 = django.db.models.TextField(
        verbose_name="Неправильный ответ 2",
        help_text="Второй неправильный ответ",
    )
    wrong_answer3 = django.db.models.TextField(
        verbose_name="Неправильный ответ 3",
        help_text="Третий неправильный ответ",
    )

    class Meta:
        verbose_name = "вопрос"
        verbose_name_plural = "вопросы"

    def __str__(self):
        return self.question


class WrongAnswer(django.db.models.Model):
    user = django.db.models.ForeignKey(
        users.models.User,
        on_delete=django.db.models.CASCADE,
        verbose_name="Пользователь",
        help_text="Пользователь, который дал неправильный ответ",
    )
    question = django.db.models.TextField(
        verbose_name="Вопрос",
        help_text="Вопрос, на который был дан неправильный ответ",
    )
    user_answer = django.db.models.TextField(
        verbose_name="Ответ пользователя",
        help_text="Ответ, который дал пользователь",
    )
    correct_answer = django.db.models.TextField(
        verbose_name="Правильный ответ", help_text="Правильный ответ на вопрос"
    )

    class Meta:
        unique_together = ("user", "question")
        verbose_name = "неправильный ответ"
        verbose_name_plural = "неправильные ответы"


class PromoCode(django.db.models.Model):
    promo_code = django.db.models.CharField(
        max_length=255,
        primary_key=True,
        verbose_name="Промокод",
        help_text="Промокод для скидки",
    )
    discount = django.db.models.IntegerField(
        verbose_name="Скидка",
        help_text="Размер скидки по промокоду (в процентах или рублях)",
    )

    class Meta:
        verbose_name = "промокод"
        verbose_name_plural = "промокоды"

    def __str__(self):
        return self.promo_code

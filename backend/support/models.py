import django.db.models

import users.models


class Chat(django.db.models.Model):
    user = django.db.models.ForeignKey(
        users.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="chats",
        verbose_name="пользователь",
    )
    topic = django.db.models.CharField(
        max_length=255, verbose_name="тема чата"
    )
    created_at = django.db.models.DateTimeField(
        auto_now_add=True, verbose_name="дата создания"
    )
    is_active = django.db.models.BooleanField(
        default=True, verbose_name="активен"
    )

    class Meta:
        verbose_name = "чат"
        verbose_name_plural = "чаты"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Чат: {self.topic} ({self.user.username})"


class Message(django.db.models.Model):
    chat = django.db.models.ForeignKey(
        Chat,
        on_delete=django.db.models.CASCADE,
        related_name="messages",
        verbose_name="чат",
    )
    user = django.db.models.ForeignKey(
        users.models.User,
        on_delete=django.db.models.CASCADE,
        related_name="messages",
        verbose_name="пользователь",
    )
    content = django.db.models.TextField(verbose_name="сообщение")
    created_at = django.db.models.DateTimeField(
        auto_now_add=True, verbose_name="дата отправки"
    )

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["created_at"]

    def __str__(self):
        return f"Сообщение от {self.user.username} в {self.chat.topic}"

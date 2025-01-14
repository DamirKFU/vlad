import django.db.models

import users.models


class ChatManager(django.db.models.Manager):
    def get_chats_for_staff(self, user, chat_type):
        if not user.is_staff:
            return self.none()

        queryset = (
            self.select_related(Chat.user.field.name)
            .prefetch_related(Chat.responsible_users.field.name)
            .all()
        )

        result = {
            "my": queryset.filter(responsible_users=user),
            "unassigned": queryset.filter(responsible_users__isnull=True),
            "assigned": queryset.filter(responsible_users__isnull=False),
        }

        return result.get(chat_type, self.none())


class Chat(django.db.models.Model):
    objects = ChatManager()
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
    updated_at = django.db.models.DateTimeField(
        auto_now=True, verbose_name="дата обновления"
    )
    responsible_users = django.db.models.ManyToManyField(
        users.models.User,
        related_name="responsible_chats",
        verbose_name="ответственные пользователи",
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
    is_system = django.db.models.BooleanField(
        default=False, verbose_name="системное сообщение"
    )

    class Meta:
        verbose_name = "сообщение"
        verbose_name_plural = "сообщения"
        ordering = ["created_at"]

    def __str__(self):
        return f"Сообщение от {self.user.username} в {self.chat.topic}"

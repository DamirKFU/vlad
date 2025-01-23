import channels.generic.websocket
import django.core.exceptions
import django.utils.timezone
import elasticsearch_dsl

import support.documents
import support.models
import users.models


class ChatConsumer(channels.generic.websocket.AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user = self.scope["user"]
        self.chat_group_name = self.get_chat_group_name(self.chat_id)

        try:
            self.chat = await self.get_chat()
            if not await self.can_access_chat():
                await self.close()
                return

            await self.channel_layer.group_add(
                self.chat_group_name, self.channel_name
            )
            await self.accept()
            await self.send_chat_history()

        except django.core.exceptions.ObjectDoesNotExist:
            await self.close()

    async def disconnect(self, close_code):
        if hasattr(self, "chat_group_name"):
            await self.channel_layer.group_discard(
                self.chat_group_name, self.channel_name
            )

    @staticmethod
    def get_chat_group_name(chat_id):
        return f"chat_{chat_id}"

    async def receive_json(self, content):
        message_type = content.get("type")

        if message_type == "chat_message":
            if not self.chat.is_active:
                await self.send_json(
                    {"type": "error", "message": "Чат неактивен"}
                )
                return

            ten_seconds_ago = (
                django.utils.timezone.now()
                - django.utils.timezone.timedelta(seconds=10)
            )
            ten_seconds_ago_iso = ten_seconds_ago.isoformat()

            messages_count = (
                support.documents.MessageDocument.search()
                .query(
                    "bool",
                    filter=[
                        elasticsearch_dsl.Q("match", user_id=self.user.id),
                        elasticsearch_dsl.Q(
                            "range", created_at={"gte": ten_seconds_ago_iso}
                        ),
                    ],
                )
                .count()
            )

            if messages_count > 10:
                await self.send_json(
                    {"type": "error", "message": "Слишком много сообщений"}
                )
                return

            message = await self.save_message(
                chat_id=self.chat_id,
                user=self.user,
                content=content.get("message", ""),
            )

            await self.send_message(message)

    async def send_message(self, message):
        await self.channel_layer.group_send(
            self.chat_group_name,
            self.message_to_json(message),
        )

    @staticmethod
    def message_to_json(message):
        return {
            "type": "chat_message",
            "message": {
                "id": message.id,
                "content": message.content,
                "user_id": message.user.id,
                "username": message.user.username,
                "created_at": message.created_at.isoformat(),
                "chat_id": message.chat_id,
                "is_system": message.is_system,
            },
        }

    async def chat_message(self, event):
        await self.send_json(event)

    async def get_chat(self):
        return await support.models.Chat.objects.select_related(
            support.models.Chat.user.field.name
        ).aget(id=self.chat_id)

    async def can_access_chat(self):
        user = self.user
        if not user.is_authenticated:
            return False

        is_author = user.id == self.chat.user_id
        is_responsible = await user.responsible_chats.filter(
            id=self.chat_id
        ).aexists()
        return is_author or is_responsible

    async def save_message(self, **kwargs):
        return await support.models.Message.objects.acreate(**kwargs)

    async def get_chat_history(self):
        messages = []
        async for message in (
            support.models.Message.objects.filter(chat_id=self.chat_id)
            .select_related(support.models.Message.user.field.name)
            .order_by(f"-{support.models.Message.created_at.field.name}")[:50]
        ):
            messages.append(message)

        return messages

    async def send_chat_history(self):
        messages = await self.get_chat_history()
        await self.send_json(
            {
                "type": "chat_history",
                "messages": [
                    {
                        "id": msg.id,
                        "content": msg.content,
                        "user_id": msg.user.id,
                        "username": msg.user.username,
                        "created_at": msg.created_at.isoformat(),
                        "is_system": msg.is_system,
                    }
                    for msg in reversed(messages)
                ],
                "user": {
                    "is_staff": self.user.is_staff,
                    "user_id": self.user.id,
                },
            }
        )

    async def get_staff_user(self):
        user = users.models.User
        return await user.objects.filter(is_staff=True).afirst()

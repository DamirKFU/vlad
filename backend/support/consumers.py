import channels.generic.websocket
import django.core.exceptions

import support.models
import users.models


class ChatConsumer(channels.generic.websocket.AsyncJsonWebsocketConsumer):
    async def connect(self):
        self.chat_id = self.scope["url_route"]["kwargs"]["chat_id"]
        self.user = self.scope["user"]
        self.chat_group_name = f"chat_{self.chat_id}"

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

    async def receive_json(self, content):
        message_type = content.get("type")

        if message_type == "chat_message":
            if not self.chat.is_active:
                await self.send_json(
                    {"type": "error", "message": "Чат неактивен"}
                )
                return

            message = await self.save_message(content.get("message", ""))

            await self.channel_layer.group_send(
                self.chat_group_name,
                {
                    "type": "chat_message",
                    "message": {
                        "id": message.id,
                        "content": message.content,
                        "user_id": message.user.id,
                        "username": message.user.username,
                        "created_at": message.created_at.isoformat(),
                        "chat_id": self.chat_id,
                    },
                },
            )

            other_user = (
                self.chat.user
                if self.user.is_staff
                else await self.get_staff_user()
            )
            if other_user:
                await self.channel_layer.group_send(
                    f"user_{other_user.id}_chats",
                    {
                        "type": "new_message",
                        "message": {
                            "chat_id": self.chat_id,
                            "content": message.content,
                            "user_id": message.user.id,
                            "username": message.user.username,
                            "created_at": message.created_at.isoformat(),
                        },
                    },
                )

    async def chat_message(self, event):
        await self.send_json(event)

    async def get_chat(self):
        return await support.models.Chat.objects.select_related("user").aget(
            id=self.chat_id,
        )

    async def can_access_chat(self):
        user = self.user
        if not user.is_authenticated:
            return False

        is_author = user.id == self.chat.user_id
        is_responsible = await user.responsible_chats.filter(
            id=self.chat_id
        ).aexists()
        return is_author or is_responsible

    async def save_message(self, content):
        return await support.models.Message.objects.acreate(
            chat_id=self.chat_id, user=self.scope["user"], content=content
        )

    async def get_chat_history(self):
        messages = []
        async for message in (
            support.models.Message.objects.filter(chat_id=self.chat_id)
            .select_related("user")
            .order_by("-created_at")[:50]
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

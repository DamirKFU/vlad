import json

import asgiref.sync
import channels.auth
import channels.testing
import django.test
import django.urls

import support.models
import support.routing
import users.models


class TestWebsocket(django.test.TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.client = django.test.Client()
        cls.user = users.models.User.objects.create_user(
            username="testuser", password="testpass"
        )
        cls.chat = support.models.Chat.objects.create(user=cls.user)
        cls.chat_message = support.models.Message.objects.create(
            chat=cls.chat, user=cls.user, content="Hello, world!"
        )
        cls.other_chat = support.models.Chat.objects.create(user=cls.user)

    @classmethod
    def tearDownClass(cls):
        users.models.User.objects.all().delete()
        super().tearDownClass()

    async def test_connect(self):
        await asgiref.sync.sync_to_async(self.client.login)(
            username=self.user.username, password="testpass"
        )
        headers = [
            (b"origin", b"..."),
            (
                b"cookie",
                self.client.cookies.output(header="", sep="; ").encode(),
            ),
        ]
        application = channels.auth.AuthMiddlewareStack(
            support.routing.websocket
        )
        communicator = channels.testing.WebsocketCommunicator(
            application,
            f"ws/support/chat/{self.chat.id}/",
            headers=headers,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)

    async def test_chat_messages(self):
        await asgiref.sync.sync_to_async(self.client.login)(
            username=self.user.username, password="testpass"
        )
        headers = [
            (b"origin", b"..."),
            (
                b"cookie",
                self.client.cookies.output(header="", sep="; ").encode(),
            ),
        ]
        application = channels.auth.AuthMiddlewareStack(
            support.routing.websocket
        )
        communicator = channels.testing.WebsocketCommunicator(
            application,
            f"ws/support/chat/{self.chat.id}/",
            headers=headers,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        event = await communicator.receive_output()
        text = json.loads(event["text"])
        self.assertEqual(text["type"], "chat_history")
        messages = text["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], self.chat_message.content)

    async def test_send_message(self):
        await asgiref.sync.sync_to_async(self.client.login)(
            username=self.user.username, password="testpass"
        )
        headers = [
            (b"origin", b"..."),
            (
                b"cookie",
                self.client.cookies.output(header="", sep="; ").encode(),
            ),
        ]
        application = channels.auth.AuthMiddlewareStack(
            support.routing.websocket
        )
        communicator = channels.testing.WebsocketCommunicator(
            application,
            f"ws/support/chat/{self.chat.id}/",
            headers=headers,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        _ = await communicator.receive_output()
        await communicator.send_json_to(
            {"type": "chat_message", "message": "Hello, world!"}
        )
        event = await communicator.receive_output(timeout=1)
        text = json.loads(event["text"])
        self.assertEqual(text["type"], "chat_message")
        self.assertEqual(text["message"]["content"], "Hello, world!")
        self.assertEqual(
            await asgiref.sync.sync_to_async(
                support.models.Message.objects.count
            )(),
            2,
        )
        communicator = channels.testing.WebsocketCommunicator(
            application,
            f"ws/support/chat/{self.other_chat.id}/",
            headers=headers,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        event = await communicator.receive_output()
        text = json.loads(event["text"])
        self.assertEqual(text["type"], "chat_history")
        messages = text["messages"]
        self.assertEqual(len(messages), 0)

    async def test_chat_messages_pagination(self):
        await asgiref.sync.sync_to_async(self.client.login)(
            username=self.user.username, password="testpass"
        )
        headers = [
            (b"origin", b"..."),
            (
                b"cookie",
                self.client.cookies.output(header="", sep="; ").encode(),
            ),
        ]
        application = channels.auth.AuthMiddlewareStack(
            support.routing.websocket
        )
        communicator = channels.testing.WebsocketCommunicator(
            application,
            f"ws/support/chat/{self.chat.id}/",
            headers=headers,
        )
        connected, _ = await communicator.connect()
        self.assertTrue(connected)
        await communicator.receive_output()
        await communicator.send_json_to(
            {"type": "get_chat_history", "page": 1}
        )
        event = await communicator.receive_output()
        text = json.loads(event["text"])
        self.assertEqual(text["type"], "chat_history")
        messages = text["messages"]
        self.assertEqual(len(messages), 1)
        self.assertEqual(messages[0]["content"], self.chat_message.content)

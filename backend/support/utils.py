import asgiref.sync
import channels.layers

import support.consumers


def send_message_to_chat(chat, message):
    channel_layer = channels.layers.get_channel_layer()
    asgiref.sync.async_to_sync(channel_layer.group_send)(
        support.consumers.ChatConsumer.get_chat_group_name(chat.id),
        support.consumers.ChatConsumer.message_to_json(message),
    )

import json
import re
from urllib.parse import unquote
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message

User = get_user_model()

def slugify_room_name(room_name):
    name = unquote(room_name)

    name = re.sub(r"[^a-zA-Z0-9_\-\.]", "_", name)

    return name

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = unquote(self.scope['url_route']['kwargs']['room_name'])
        slug_room_name = slugify_room_name(self.room_name)
        self.room_group_name = f'chat_{slug_room_name}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()

        # Send room info
        room = await self.get_room()
        if room:
            await self.send(text_data=json.dumps({
                'type': 'room_info',
                'room_name': room.name,
                'room_id': room.id
            }))

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = text_data_json['message']
            user = self.scope['user']

            if user.is_authenticated:
                # Save message to database
                room = await self.get_room()
                if room:
                    saved_message = await self.save_message(room, user, message)

                    # Send message to room group
                    await self.channel_layer.group_send(
                        self.room_group_name,
                        {
                            'type': 'chat_message',
                            'message': message,
                            'user_id': user.id,
                            'username': user.username,
                            'message_id': saved_message.id,
                            'timestamp': saved_message.timestamp.isoformat(),
                        }
                    )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'user_id': event['user_id'],
            'username': event['username'],
            'message_id': event['message_id'],
            'timestamp': event['timestamp'],
        }))

    @database_sync_to_async
    def get_room(self):
        try:
            return ChatRoom.objects.get(name=self.room_name)
        except ChatRoom.DoesNotExist:
            return None

    @database_sync_to_async
    def save_message(self, room, user, content):
        return Message.objects.create(
            room=room,
            user=user,
            content=content
        )


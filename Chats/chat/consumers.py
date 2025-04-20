import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, Message, UserProfile
from datetime import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        # Update user status
        await self.update_user_status(True)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Update user status
        await self.update_user_status(False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type', 'chat_message')

        if message_type == 'chat_message':
            message = data.get('message', '')
            username = data.get('username', '')

            # Save message to database
            await self.save_message(username, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username
                }
            )
        elif message_type == 'call_offer':
            # Handle incoming call offer
            offer = data.get('offer')
            is_video = data.get('is_video', True)
            username = data.get('username', '')

            # Send call offer to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_offer',
                    'offer': offer,
                    'is_video': is_video,
                    'username': username
                }
            )
        elif message_type == 'call_answer':
            # Handle call answer
            answer = data.get('answer')

            # Send call answer to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_answer',
                    'answer': answer
                }
            )
        elif message_type == 'ice_candidate':
            # Handle ICE candidate
            candidate = data.get('candidate')

            # Send ICE candidate to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'candidate': candidate
                }
            )
        elif message_type == 'call_ended':
            # Handle call end
            username = data.get('username', '')

            # Send call ended to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'call_ended',
                    'username': username
                }
            )

    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'username': event['username']
        }))

    async def call_offer(self, event):
        # Send call offer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_offer',
            'offer': event['offer'],
            'is_video': event['is_video'],
            'username': event['username']
        }))

    async def call_answer(self, event):
        # Send call answer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_answer',
            'answer': event['answer']
        }))

    async def ice_candidate(self, event):
        # Send ICE candidate to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate']
        }))

    async def call_ended(self, event):
        # Send call ended to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'username': event['username']
        }))

    @database_sync_to_async
    def save_message(self, username, message):
        user = get_user_model().objects.get(username=username)
        room = ChatRoom.objects.get(name=self.room_name)
        Message.objects.create(
            room=room,
            sender=user,
            content=message,
            timestamp=datetime.now()
        )

    @database_sync_to_async
    def update_user_status(self, is_online):
        user_id = self.user.id
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)
        profile.is_online = is_online
        profile.last_seen = datetime.now()
        profile.save()

class CallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'call_{self.room_name}'
        self.user = self.scope['user']

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        await self.update_user_status(True)

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        await self.update_user_status(False)

    async def receive(self, text_data):
        data = json.loads(text_data)
        
        # Handle different message types
        if 'type' in data:
            if data['type'] == 'call_offer':
                # Forward call offer to other users in the room
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_offer',
                        'offer': data['offer'],
                        'is_video': data['is_video'],
                        'username': self.user.username
                    }
                )
            elif data['type'] == 'call_answer':
                # Forward call answer to the caller
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_answer',
                        'answer': data['answer'],
                        'username': self.user.username
                    }
                )
            elif data['type'] == 'ice_candidate':
                # Forward ICE candidate to other users
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'ice_candidate',
                        'candidate': data['candidate'],
                        'username': self.user.username
                    }
                )
            elif data['type'] == 'call_rejected':
                # Notify that call was rejected
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_rejected',
                        'username': self.user.username
                    }
                )
            elif data['type'] == 'call_ended':
                # Notify that call has ended
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_ended',
                        'username': self.user.username
                    }
                )

    async def call_offer(self, event):
        # Send call offer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_offer',
            'offer': event['offer'],
            'is_video': event['is_video'],
            'username': event['username']
        }))
    
    async def call_answer(self, event):
        # Send call answer to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_answer',
            'answer': event['answer'],
            'username': event['username']
        }))
    
    async def ice_candidate(self, event):
        # Send ICE candidate to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'ice_candidate',
            'candidate': event['candidate'],
            'username': event['username']
        }))
    
    async def call_rejected(self, event):
        # Send call rejected notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_rejected',
            'username': event['username']
        }))
    
    async def call_ended(self, event):
        # Send call ended notification to WebSocket
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'username': event['username']
        }))

    @database_sync_to_async
    def update_user_status(self, is_online):
        user_id = self.user.id
        profile, created = UserProfile.objects.get_or_create(user_id=user_id)
        profile.is_online = is_online
        profile.last_seen = datetime.now()
        profile.save() 
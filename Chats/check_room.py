import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')
django.setup()

from django.contrib.auth import get_user_model
from chat.models import ChatRoom

User = get_user_model()

def check_and_create_room():
    # Get or create test users
    user1, _ = User.objects.get_or_create(username='testuser1')
    user2, _ = User.objects.get_or_create(username='testuser2')
    
    # Create room name
    room_name = f'chat_{user1.id}_{user2.id}'
    
    # Check if room exists
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={
            'is_group': False
        }
    )
    
    if created:
        room.participants.add(user1, user2)
        print(f"Created new chat room: {room_name}")
    else:
        print(f"Chat room already exists: {room_name}")
    
    return room

if __name__ == '__main__':
    check_and_create_room() 
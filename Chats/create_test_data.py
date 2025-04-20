import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')
django.setup()

from django.contrib.auth.models import User
from chat.models import ChatRoom, UserProfile

def create_test_data():
    print("Creating test data...")
    
    # Create admin user if not exists
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@example.com',
            'is_staff': True,
            'is_superuser': True
        }
    )
    if created:
        admin_user.set_password('admin')
        admin_user.save()
        print("Created admin user")
    else:
        print("Admin user already exists")
    
    # Create test user if not exists
    test_user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com'
        }
    )
    if created:
        test_user.set_password('test')
        test_user.save()
        print("Created test user")
    else:
        print("Test user already exists")
    
    # Create user profiles
    UserProfile.objects.get_or_create(user=admin_user)
    UserProfile.objects.get_or_create(user=test_user)
    
    # Create test chat room
    room_name = 'chat_1_2'
    room, created = ChatRoom.objects.get_or_create(
        name=room_name,
        defaults={
            'created_at': django.utils.timezone.now()
        }
    )
    if created:
        room.participants.add(admin_user, test_user)
        print(f"Created chat room: {room_name}")
    else:
        print(f"Chat room {room_name} already exists")
    
    print("Test data setup completed!")

if __name__ == '__main__':
    create_test_data() 
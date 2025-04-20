import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'messenger.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_test_user():
    # Create test user if not exists
    user, created = User.objects.get_or_create(
        username='testuser1',
        defaults={
            'email': 'testuser1@example.com',
            'is_staff': True  # Allow admin login
        }
    )
    
    # Set password
    user.set_password('testuser1')
    user.save()
    
    if created:
        print("Created test user: testuser1")
    else:
        print("Updated test user: testuser1")
    
    return user

if __name__ == '__main__':
    create_test_user() 
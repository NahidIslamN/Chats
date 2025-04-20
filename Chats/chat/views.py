from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from .models import ChatRoom, Message, UserProfile
from django.db.models import Q
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
import os
from django.conf import settings

@login_required
def chat_list(request):
    # Get all chat rooms where the user is a participant
    chat_rooms = ChatRoom.objects.filter(participants=request.user)
    return render(request, 'chat/chat_list.html', {'chat_rooms': chat_rooms})

@login_required
def chat_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name, participants=request.user)
    messages = Message.objects.filter(room=room).order_by('timestamp')
    participants = room.participants.all()
    
    # Mark messages as read
    messages.filter(~Q(sender=request.user), is_read=False).update(is_read=True)
    
    return render(request, 'chat/chat_room.html', {
        'room': room,
        'messages': messages,
        'participants': participants,
    })

@login_required
def create_chat(request):
    if request.method == 'POST':
        user_id = request.POST.get('user_id')
        other_user = get_object_or_404(User, id=user_id)
        
        # Check if chat room already exists
        existing_room = ChatRoom.objects.filter(
            participants=request.user
        ).filter(
            participants=other_user
        ).filter(
            is_group=False
        ).first()
        
        if existing_room:
            return redirect('chat:chat_room', room_name=existing_room.name)
        
        # Create new chat room
        room = ChatRoom.objects.create(name=f'chat_{request.user.id}_{other_user.id}')
        room.participants.add(request.user, other_user)
        
        return redirect('chat:chat_room', room_name=room.name)
    
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/create_chat.html', {'users': users})

@login_required
def user_list(request):
    users = User.objects.exclude(id=request.user.id)
    return render(request, 'chat/user_list.html', {'users': users})

@login_required
def user_profile(request, username):
    user = get_object_or_404(User, username=username)
    profile, created = UserProfile.objects.get_or_create(user=user)
    return render(request, 'chat/user_profile.html', {'profile': profile})

@login_required
def update_profile(request):
    if request.method == 'POST':
        profile = request.user.profile
        profile.status = request.POST.get('status', profile.status)
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']
        profile.save()
        return redirect('chat:user_profile', username=request.user.username)
    return render(request, 'chat/update_profile.html')

@login_required
def call_room(request, room_name):
    room = get_object_or_404(ChatRoom, name=room_name, participants=request.user)
    return render(request, 'chat/call_room.html', {
        'room': room,
        'room_name': room_name
    })

@login_required
@csrf_protect
def upload_file(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST requests are allowed'}, status=405)
    
    if 'file' not in request.FILES:
        return JsonResponse({'error': 'No file was uploaded'}, status=400)
    
    uploaded_file = request.FILES['file']
    file_type = uploaded_file.content_type.split('/')[0]
    
    if file_type not in ['image', 'video', 'audio']:
        return JsonResponse({'error': 'Invalid file type'}, status=400)
    
    # Create the media directory if it doesn't exist
    upload_dir = os.path.join(settings.MEDIA_ROOT, 'chat_files', str(request.user.id))
    os.makedirs(upload_dir, exist_ok=True)
    
    # Save the file
    file_path = os.path.join(upload_dir, uploaded_file.name)
    with open(file_path, 'wb+') as destination:
        for chunk in uploaded_file.chunks():
            destination.write(chunk)
    
    # Return the file URL
    file_url = f'/media/chat_files/{request.user.id}/{uploaded_file.name}'
    return JsonResponse({'file_url': file_url}) 
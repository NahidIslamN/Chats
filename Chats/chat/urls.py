from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    path('', views.chat_list, name='chat_list'),
    path('room/<str:room_name>/', views.chat_room, name='chat_room'),
    path('call/<str:room_name>/', views.call_room, name='call_room'),
    path('create/', views.create_chat, name='create_chat'),
    path('users/', views.user_list, name='user_list'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
    path('profile/update/', views.update_profile, name='update_profile'),
    path('upload/', views.upload_file, name='upload_file'),
] 
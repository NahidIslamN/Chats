@echo off
echo Starting Django server with WebSocket support...
set DJANGO_SETTINGS_MODULE=messenger.settings
C:\Users\nnnn1\AppData\Local\Programs\Python\Python313\python.exe -m daphne -b 0.0.0.0 -p 8000 messenger.asgi:application
pause 
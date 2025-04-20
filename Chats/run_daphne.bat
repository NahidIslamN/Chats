@echo off
echo Setting up environment...
set PYTHONPATH=%cd%
set DJANGO_SETTINGS_MODULE=messenger.settings

echo Checking for existing processes on port 8000...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a
    taskkill /F /PID %%a
)

echo Starting Daphne server...
C:\Users\nnnn1\AppData\Local\Programs\Python\Python313\python.exe -m daphne --access-log - --verbosity 2 -b 0.0.0.0 -p 8000 messenger.asgi:application

echo Server stopped. Press any key to exit...
pause 
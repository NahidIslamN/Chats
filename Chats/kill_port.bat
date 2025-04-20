@echo off
echo Finding processes using port 8000...

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8000') do (
    echo Killing process %%a
    taskkill /F /PID %%a
)

echo Done. Press any key to exit...
pause 
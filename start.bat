@echo off

echo Installing pip
call "%CD%\python.exe" get-pip.py

echo Installing dependencies
call "%CD%\python.exe" -m pip install VehicleDetectionTracker

echo Installing Websockets
call "%CD%\python.exe" -m pip install -r examples/requirements.txt

if %errorlevel% neq 0 (
    echo Failed to install dependencies.
    timeout /t 3 /nobreak
    exit /b %errorlevel%
)

echo Running...
call "%CD%\python.exe" server.py

:: Check if npm run dev was successful
if %errorlevel% neq 0 (
    echo Run failed.
    timeout /t 3 /nobreak
    exit /b %errorlevel%
)

echo Script executed successfully.
pause

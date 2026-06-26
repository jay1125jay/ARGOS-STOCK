@echo off
title ARGOS STOCK CONTROL
color 0A

:MENU
cls
echo ==========================================
echo        ARGOS STOCK CONTROL CENTER
echo ==========================================
echo.
echo 1. Start ARGOS CORE + DASHBOARD
echo 2. Stop ARGOS
echo 3. Open Dashboard
echo 4. Check Status
echo 5. Push GitHub
echo 6. Exit
echo.
set /p choice=Select option: 

if "%choice%"=="1" goto START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto OPEN
if "%choice%"=="4" goto STATUS
if "%choice%"=="5" goto PUSH
if "%choice%"=="6" exit
goto MENU

:START
cd /d C:\ARGOS_STOCK
start "ARGOS CORE" cmd /k py auto_loop.py
timeout /t 2 > nul
start "ARGOS DASHBOARD" cmd /k py app_server.py
timeout /t 2 > nul
start http://localhost:8000
pause
goto MENU

:STOP
taskkill /F /IM python.exe
echo ARGOS STOPPED
pause
goto MENU

:OPEN
start http://localhost:8000
pause
goto MENU

:STATUS
cd /d C:\ARGOS_STOCK
echo.
echo === GIT STATUS ===
git status
echo.
echo === OPEN POSITIONS ===
type data\open_positions.json
echo.
echo === LAST TRADES ===
powershell -Command "Get-Content data\trades\paper_trades.csv -Tail 5"
pause
goto MENU

:PUSH
cd /d C:\ARGOS_STOCK
git add .
git commit -m "Update ARGOS STOCK"
git push
echo PUSH COMPLETE
pause
goto MENU

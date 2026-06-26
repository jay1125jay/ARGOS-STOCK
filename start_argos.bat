@echo off
cd /d C:\ARGOS_STOCK

start "ARGOS CORE" cmd /k py auto_loop.py
timeout /t 2 > nul

start "ARGOS DASHBOARD" cmd /k py app_server.py
timeout /t 2 > nul

start http://localhost:8000

exit

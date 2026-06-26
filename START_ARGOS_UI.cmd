@echo off
cd /d C:\ARGOS_STOCK
start cmd /k python app_server.py
start http://localhost:8000

@echo off
cd /d C:\ARGOS_STOCK

git status
git add .

git commit -m "Update ARGOS STOCK"
git push

echo ARGOS PUSH COMPLETE
pause

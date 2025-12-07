@echo off
echo Running chat migrations...
cd national_parks
python manage.py migrate chat
echo.
echo If you see errors, make sure:
echo 1. Virtual environment is activated
echo 2. You're in the correct directory
echo 3. Django is installed
echo.
pause


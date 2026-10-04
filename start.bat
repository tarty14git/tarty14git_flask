@echo off
echo Starting CTH Enterprise Flask Application (Windows Waitress Server)...
call venv\Scripts\activate.bat
waitress-serve --port=5000 wsgi:app

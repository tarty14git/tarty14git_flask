@echo off
echo ===================================================
echo  CTH Enterprise Flask Application Build Script
echo ===================================================

echo [1/3] Setting up Python virtual environment...
python -m venv venv
call venv\Scripts\activate.bat

echo [2/3] Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo [3/3] Initializing Database and Application Objects...
python -c "from app import create_app; app = create_app(); print('Build and database initialization complete!')"

echo ===================================================
echo  Build Successful! Run start.bat to start server.
echo ===================================================

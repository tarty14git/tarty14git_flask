#!/bin/bash
echo "==================================================="
echo " Starting CTH Enterprise Flask Application (Linux) "
echo "==================================================="

if [ ! -d "venv" ]; then
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

nohup gunicorn --workers 4 --bind 0.0.0.0:5000 wsgi:app > app.log 2>&1 &
echo $! > app.pid
echo "Application started in background with PID $(cat app.pid). Logs: app.log"

#!/bin/bash
echo "Stopping CTH Enterprise Flask Application..."
if [ -f "app.pid" ]; then
    PID=$(cat app.pid)
    kill -9 $PID 2>/dev/null
    rm -f app.pid
    echo "Process $PID terminated."
else
    pkill -f gunicorn 2>/dev/null
    echo "Gunicorn process stopped."
fi

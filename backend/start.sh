#!/bin/bash

# Start Xvfb
Xvfb :99 -screen 0 1280x1024x24 > /dev/null 2>&1 &

# Wait for Xvfb to start
sleep 1

# Run Django commands
python manage.py migrate
python manage.py collectstatic --noinput

# Start Gunicorn
gunicorn backend.wsgi:application --bind 0.0.0.0:$PORT --log-file - 
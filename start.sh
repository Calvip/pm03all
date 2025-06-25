#!/bin/sh
cd "$(dirname "$0")"
if [ -d ".venv" ]; then
    echo ".venv found!"
else
    echo ".venv not found!"
    echo "installing .venv..."
    /sbin/python -m venv .venv 
    echo "installing dependencies..."
    .venv/bin/pip install -r requirements.txt
fi
echo "running web module..."
.venv/bin/python -m flask run --host=0.0.0.0
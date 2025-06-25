#!/bin/sh
cd "$(dirname "$0")"

echo "Installing dependencies (if needed)..."
pip install -r requirements.txt

echo "Running web module..."
python -m flask run --host=0.0.0.0
#!/bin/bash

echo "Starting setup..."

cd /

# install dependencies
echo "updating pip..."
/venv/bin/pip install --upgrade pip

echo "Installing dependencies..."
/venv/bin/pip install -r /requirements.txt


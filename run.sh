#!/bin/bash
# MyImpression Run Script
# Activates virtual environment and runs the application

echo "Starting MyImpression..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Please run install.sh first."
    exit 1
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Run the application
echo "Starting application..."
python main.py

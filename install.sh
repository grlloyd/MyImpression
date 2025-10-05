#!/bin/bash
# MyImpression Installation Script
# Sets up virtual environment and installs dependencies

echo "MyImpression Installation Script"
echo "================================"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    echo "Please install Python 3 first:"
    echo "  sudo apt update"
    echo "  sudo apt install python3 python3-pip python3-venv"
    exit 1
fi

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Inky library (if available)
echo "Installing Inky library..."
if [ -d "../inky" ]; then
    echo "Installing Inky from local directory..."
    pip install -e ../inky
else
    echo "Installing Inky from PyPI..."
    pip install inky
fi

# Run setup
echo "Running setup..."
python setup.py

echo ""
echo "Installation complete!"
echo ""
echo "To run the application:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the application: python main.py"
echo ""
echo "To deactivate the virtual environment later: deactivate"

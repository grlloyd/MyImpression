# Installation Guide

## Quick Start (Recommended)

### 1. Run the Installation Script
```bash
chmod +x install.sh
./install.sh
```

### 2. Run the Application
```bash
chmod +x run.sh
./run.sh
```

## Manual Installation

### 1. Create Virtual Environment
```bash
python3 -m venv venv
```

### 2. Activate Virtual Environment
```bash
source venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Install Inky Library
If you have the Inky library in a sibling directory:
```bash
pip install -e ../inky
```

Or install from PyPI:
```bash
pip install inky
```

### 5. Run Setup
```bash
python setup.py
```

### 6. Run Application
```bash
python main.py
```

## Troubleshooting

### Virtual Environment Issues
If you get permission errors:
```bash
sudo apt install python3-venv python3-full
```

### GPIO Access Issues
If buttons don't work, you may need to run with sudo:
```bash
sudo ./run.sh
```

### Display Not Found
Make sure the Inky library is properly installed and the display is connected.

## Deactivating Virtual Environment
When you're done:
```bash
deactivate
```

## Reinstalling
To start fresh:
```bash
rm -rf venv
./install.sh
```

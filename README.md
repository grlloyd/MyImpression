# MyImpression - 4-Mode Display System

A customizable display system for the 6-color Inky Impression e-ink display (800x480, 127 DPI).

## Features

- **Photo Cycle Mode**: Slideshow of photos from a configured folder
- **Weather Dashboard**: Real-time weather information (planned)
- **Solar Monitor**: Solar panel output monitoring (planned)
- **News Feed**: Scientific publications feed (planned)

## Hardware Requirements

- 6-color Inky Impression display (800x480, 127 DPI)
- Raspberry Pi (recommended)
- 4 buttons for mode switching

## Installation

### Quick Start (Recommended)
```bash
chmod +x install.sh
./install.sh
```

### Manual Installation

1. Create and activate a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```

2. Install Python dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

3. Install the Inky library:
```bash
# If you have the Inky library in a sibling directory:
pip install -e ../inky

# Or install from PyPI:
pip install inky
```

4. Run setup:
```bash
python setup.py
```

5. Configure your settings in `config.json`

## Configuration

The system uses a JSON configuration file (`config.json`) to manage all settings:

```json
{
  "display": {
    "resolution": [800, 480],
    "dpi": 127,
    "colors": 6,
    "refresh_rate": 30
  },
  "buttons": {
    "A": "photo_cycle",
    "B": "weather",
    "C": "solar_monitor",
    "D": "news_feed"
  },
  "photo_cycle": {
    "folder": "./data/photos",
    "display_time": 10,
    "random_order": false,
    "supported_formats": ["jpg", "jpeg", "png", "webp"],
    "background_color": "white"
  }
}
```

## Service Installation (Auto-Start on Boot)

To run MyImpression automatically when the Pi boots:

```bash
sudo chmod +x install_service.sh
sudo ./install_service.sh
```

This installs MyImpression as a systemd service that:
- Starts automatically on boot
- Restarts if it crashes
- Runs in the background
- Can be managed with standard systemctl commands

See `SERVICE_SETUP.md` for detailed service management instructions.

## Usage

### Photo Cycle Mode (Currently Implemented)

1. Place your photos in the `data/photos` folder
2. Supported formats: JPG, JPEG, PNG, WebP
3. Press button A to start/switch to photo cycle mode
4. Photos will cycle automatically based on the `display_time` setting
5. Background color for image bars can be set in `config.json`

### Running the Application

**Using the run script (recommended):**
```bash
chmod +x run.sh
./run.sh
```

**Or manually:**
```bash
source venv/bin/activate
python main.py
```

The application will:
- Initialize the display
- Start button monitoring
- Begin with photo cycle mode
- Switch modes when buttons are pressed

## File Structure

```
MyImpression/
├── main.py                 # Main application
├── config.json             # Configuration file
├── requirements.txt        # Python dependencies
├── modules/                # Core modules
│   ├── __init__.py
│   ├── button_handler.py   # GPIO button management
│   ├── photo_cycle.py      # Photo slideshow mode
│   ├── weather_dashboard.py # Weather display (placeholder)
│   ├── solar_monitor.py    # Solar monitoring (placeholder)
│   ├── news_feed.py        # News feed (placeholder)
│   └── display_utils.py    # Display utilities
├── data/
│   ├── photos/             # Photo cycle images
│   └── cache/              # API response cache
└── assets/
    ├── fonts/              # Font files
    └── icons/              # Icon files
```

## Development Status

- ✅ **Photo Cycle Mode**: Fully implemented
- ⏳ **Weather Dashboard**: Placeholder (to be implemented)
- ⏳ **Solar Monitor**: Placeholder (to be implemented)
- ⏳ **News Feed**: Placeholder (to be implemented)

## Troubleshooting

### No Photos Found
- Ensure photos are in the `data/photos` folder
- Check that file formats are supported (JPG, PNG, WebP)
- Verify file permissions

### Button Not Working
- Check GPIO configuration
- Ensure proper hardware connections
- Run with `sudo` if needed for GPIO access

### Display Issues
- Verify Inky library installation
- Check display connections
- Ensure proper power supply

## License

This project is open source. See individual module licenses for details.

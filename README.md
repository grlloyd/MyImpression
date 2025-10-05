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

1. Install Python dependencies:
```bash
pip install -r requirements.txt
```

2. Install the Inky library:
```bash
cd ../inky
pip install -e .
```

3. Configure your settings in `config.json`

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

## Usage

### Photo Cycle Mode (Currently Implemented)

1. Place your photos in the `data/photos` folder
2. Supported formats: JPG, JPEG, PNG, WebP
3. Press button A to start/switch to photo cycle mode
4. Photos will cycle automatically based on the `display_time` setting
5. Background color for image bars can be set in `config.json`

### Running the Application

```bash
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

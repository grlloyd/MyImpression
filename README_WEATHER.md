# Weather Mode for MyImpression

This document describes the new Weather Mode added to the MyImpression display system.

## Overview

The Weather Mode displays current weather conditions, a 5-day forecast, and hourly weather predictions using data from the Open-Meteo API. The display is optimized for the 6-color Inky Impression e-ink display (800x480 resolution).

## Features

- **Current Weather**: Large weather icon, temperature, and conditions
- **5-Day Forecast**: Daily weather icons with high/low temperatures
- **Hourly Forecast**: 12-hour timeline with weather icons and temperatures
- **Automatic Updates**: Configurable update intervals with intelligent caching
- **Error Handling**: Graceful fallbacks for network issues or API failures
- **E-ink Optimized**: High contrast icons and text for optimal readability

## Display Layout

```
┌─────────────────────────────────────────────────────────┐
│  TODAY'S WEATHER    │  5-DAY FORECAST                  │
│  ┌─────────────┐    │  ┌───┐ ┌───┐ ┌───┐ ┌───┐ ┌───┐  │
│  │   ☀️ 22°C   │    │  │☀️ │ │☁️ │ │🌧️ │ │❄️ │ │⛈️ │  │
│  │  Sunny      │    │  │25°│ │28°│ │18°│ │5° │ │30°│  │
│  │             │    │  │15°│ │20°│ │12°│ │-2°│ │25°│  │
│  └─────────────┘    │  └───┘ └───┘ └───┘ └───┘ └───┘  │
├─────────────────────────────────────────────────────────┤
│  HOURLY FORECAST: ☀️ ☁️ ☁️ 🌧️ 🌧️ ☁️ ☀️ ☀️ ☀️ ☁️ ☁️ 🌧️  │
│  12p  1p  2p  3p  4p  5p  6p  7p  8p  9p 10p 11p      │
└─────────────────────────────────────────────────────────┘
```

## Configuration

Add the following section to your `config.json`:

```json
{
  "weather": {
    "latitude": 51.5074,
    "longitude": -0.1278,
    "display_time": 300,
    "update_interval": 1800,
    "cache_duration": 3600
  }
}
```

### Configuration Options

- **latitude**: Your location's latitude (default: London)
- **longitude**: Your location's longitude (default: London)
- **display_time**: How long to show weather before allowing mode switch (seconds)
- **update_interval**: How often to fetch new data from API (seconds)
- **cache_duration**: How long to keep cached data (seconds)

## Button Mapping

The weather mode is mapped to **Button D** (button_4) by default. You can change this in the `buttons` section of your config:

```json
{
  "buttons": {
    "button_1": "photo_cycle",
    "button_2": "tumblr_rss", 
    "button_3": "deviantart_rss",
    "button_4": "weather"
  }
}
```

## Weather Icons

The system generates weather icons based on Open-Meteo's weather codes:

- **0-1**: Clear/Sunny (☀️)
- **2-3**: Partly Cloudy/Overcast (☁️)
- **45-48**: Fog (🌫️)
- **51-67**: Rain (🌧️)
- **71-77**: Snow (❄️)
- **80-87**: Rain Showers (🌦️)
- **95-99**: Thunderstorms (⛈️)

## API Information

The weather mode uses the [Open-Meteo API](https://open-meteo.com/), which provides:
- Free weather data (no API key required)
- High-quality forecasts
- Global coverage
- Reliable uptime

## Files Added/Modified

### New Files
- `modules/weather.py` - Main weather mode class
- `modules/weather_api.py` - Open-Meteo API client
- `test_weather.py` - Test script for weather functionality

### Modified Files
- `main.py` - Added weather mode to mode registry and configuration
- `config.json` - Added weather configuration (auto-generated if missing)

## Testing

Run the test script to verify weather functionality:

```bash
python test_weather.py
```

This will test:
- API connectivity and data fetching
- Weather icon generation
- Display layout generation
- Error handling

## Usage

1. **Configure Location**: Update the `latitude` and `longitude` in your config
2. **Start Application**: Run `python main.py` as usual
3. **Switch to Weather**: Press Button D to switch to weather mode
4. **View Weather**: The display will show current conditions and forecasts
5. **Automatic Updates**: Weather data updates automatically based on your configuration

## Troubleshooting

### No Weather Data
- Check your internet connection
- Verify latitude/longitude coordinates
- Check the cache file at `data/cache/weather_data.json`

### Display Issues
- Ensure you're using a 6-color Inky Impression display
- Check that the display resolution is 800x480
- Verify PIL/Pillow is properly installed

### API Errors
- Open-Meteo API is free but has rate limits
- Check your network connectivity
- The system will use cached data as fallback

## Performance

- **API Calls**: Minimized through intelligent caching
- **Display Updates**: Only when data changes or display time expires
- **Memory Usage**: Efficient image generation and cleanup
- **Battery Life**: Optimized for e-ink display characteristics

## Future Enhancements

Potential improvements for future versions:
- Multiple location support
- Weather alerts and warnings
- Historical weather data
- Custom weather icon sets
- Weather trend indicators
- Location-based automatic updates

# Weather Icon Configuration

The weather display supports three different icon sources that can be configured in your `config.json` file.

## Configuration Options

In your `config.json` file, add a `weather_html` section with the following options:

```json
{
  "weather_html": {
    "icon_source": "emoji",
    "custom_icon_path": "assets/icons/weather/",
    "update_interval": 1800
  }
}
```

### Icon Source Options

#### 1. Emoji Icons (Default)
```json
"icon_source": "emoji"
```
- Uses Unicode emoji characters (☀️, ☁️, 🌧️, etc.)
- No additional dependencies required
- Good contrast on e-ink displays
- Works out of the box

#### 2. Font Awesome Icons
```json
"icon_source": "fontawesome"
```
- Uses Font Awesome icon classes (fas fa-sun, fas fa-cloud, etc.)
- Requires Font Awesome CSS to be loaded
- More professional appearance
- Fallback to emoji if Font Awesome not available

#### 3. Custom Icons
```json
"icon_source": "custom"
```
- Uses custom PNG icon files
- Place your icon files in the `custom_icon_path` directory
- Icon files should be named with weather codes (0.png, 1.png, 3.png, etc.)
- Falls back to Font Awesome, then emoji if custom icons not found

### Custom Icon Setup

If you choose `"icon_source": "custom"`, you need to:

1. Create the custom icon directory:
   ```bash
   mkdir -p assets/icons/weather/
   ```

2. Add PNG icon files named with weather codes:
   ```
   assets/icons/weather/
   ├── 0.png    # Clear sky
   ├── 1.png    # Mainly clear
   ├── 2.png    # Partly cloudy
   ├── 3.png    # Overcast
   ├── 45.png   # Fog
   ├── 51.png   # Light drizzle
   ├── 61.png   # Slight rain
   ├── 71.png   # Slight snow
   ├── 80.png   # Rain showers
   ├── 95.png   # Thunderstorm
   └── ...
   ```

3. Icon specifications:
   - Format: PNG with transparency
   - Size: Recommended 64x64px or larger
   - Style: High contrast, suitable for e-ink displays
   - Naming: Use weather codes from Open-Meteo API

### Weather Codes Reference

| Code | Description | Example Icon |
|------|-------------|--------------|
| 0 | Clear sky | ☀️ |
| 1 | Mainly clear | ☀️ |
| 2 | Partly cloudy | ⛅ |
| 3 | Overcast | ☁️ |
| 45 | Fog | 🌫️ |
| 48 | Depositing rime fog | 🌫️ |
| 51 | Light drizzle | 🌦️ |
| 53 | Moderate drizzle | 🌦️ |
| 55 | Dense drizzle | 🌦️ |
| 61 | Slight rain | 🌧️ |
| 63 | Moderate rain | 🌧️ |
| 65 | Heavy rain | 🌧️ |
| 71 | Slight snow fall | ❄️ |
| 73 | Moderate snow fall | ❄️ |
| 75 | Heavy snow fall | ❄️ |
| 80 | Slight rain showers | 🌧️ |
| 81 | Moderate rain showers | 🌧️ |
| 82 | Violent rain showers | 🌧️ |
| 85 | Slight snow showers | 🌨️ |
| 86 | Heavy snow showers | 🌨️ |
| 95 | Thunderstorm | ⛈️ |
| 96 | Thunderstorm with slight hail | ⛈️ |
| 99 | Thunderstorm with heavy hail | ⛈️ |

### Configuration Examples

#### Example 1: Emoji Icons (Default)
```json
{
  "weather_html": {
    "icon_source": "emoji",
    "update_interval": 1800
  }
}
```

#### Example 2: Font Awesome Icons
```json
{
  "weather_html": {
    "icon_source": "fontawesome",
    "update_interval": 1800
  }
}
```

#### Example 3: Custom Icons
```json
{
  "weather_html": {
    "icon_source": "custom",
    "custom_icon_path": "assets/icons/weather/",
    "update_interval": 1800
  }
}
```

### Fallback Behavior

The icon system uses a fallback hierarchy:

1. **Custom Icons**: If `icon_source` is "custom" and icon file exists
2. **Font Awesome**: If Font Awesome is available and configured
3. **Emoji**: Always available as final fallback

This ensures the weather display always shows some form of icon, even if your preferred source is unavailable.

### Testing Your Configuration

To test your icon configuration:

1. Update your `config.json` file
2. Run the weather display test:
   ```bash
   python test_weather_html.py
   ```
3. Check the generated `test_weather_output.png` file
4. Or open `weather_test_new_layout.html` in your browser

The system will log which icon source is being used when it starts up.

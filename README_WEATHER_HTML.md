# HTML Weather Mode

A modern, HTML-based weather display for the MyImpression e-ink display system. This mode uses HTML templates and browser automation to create beautiful, professional-looking weather displays.

## Features

- **Modern Design**: Clean, card-based layout with gradients and shadows
- **Professional Typography**: Uses Inter font family for better readability
- **Weather Icons**: Font Awesome icons for consistent weather representation
- **Responsive Layout**: Optimized for 800x480 e-ink display
- **Current Weather**: Large temperature display with conditions
- **5-Day Forecast**: Compact daily forecast with high/low temperatures
- **12-Hour Forecast**: Horizontal scrolling hourly forecast
- **Fallback Support**: Graceful degradation if browser automation fails

## Architecture

### Components

1. **HTML Template** (`templates/weather.html`)
   - Jinja2 template with embedded JavaScript
   - Weather data injection
   - Responsive layout structure

2. **CSS Stylesheet** (`templates/weather.css`)
   - Modern CSS with Flexbox/Grid layouts
   - Optimized for e-ink display colors
   - Responsive design principles

3. **Python Module** (`modules/weather_html.py`)
   - HTML generation and browser automation
   - Playwright integration for screen capture
   - Fallback rendering with PIL

4. **Integration** (`main.py`)
   - Added as `weather_html` mode
   - Button 4 mapped to HTML weather mode
   - LED pattern: 5 flashes

### Dependencies

- **jinja2**: HTML template rendering
- **playwright**: Browser automation for screen capture
- **Pillow**: Image processing and fallback rendering

## Installation

1. Install new dependencies:
   ```bash
   pip install jinja2 playwright
   ```

2. Install Playwright browsers:
   ```bash
   playwright install chromium
   ```

3. The HTML weather mode is automatically available as `weather_html`

## Usage

### Button Control
- **Button 4**: Switch to HTML weather mode
- **LED Pattern**: 5 flashes when entering mode

### Configuration
The HTML weather mode uses the same configuration as the standard weather mode:

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

### Testing
Run the test script to verify functionality:

```bash
python test_weather_html.py
```

This will:
- Test HTML generation
- Attempt browser rendering (if Playwright is available)
- Fall back to basic rendering if needed
- Save output as `test_weather_output.png`

## Design Features

### Visual Improvements
- **Gradient Backgrounds**: Beautiful color gradients for current weather
- **Card Layout**: Clean, modern card-based design
- **Typography Hierarchy**: Clear visual hierarchy with different font weights
- **Color Coding**: Temperature-based color coding (red for high, blue for low)
- **Weather Icons**: Professional weather iconography
- **Spacing**: Proper spacing and padding for better readability

### Layout Structure
```
┌─────────────────────────────────────────────────────────┐
│  Current Weather (Gradient Background)                  │
│  ☀️ 22°C Clear sky                                      │
│  Feels like 24°C | Wind 12 km/h | Humidity 65%         │
├─────────────────────────────────────────────────────────┤
│  5-Day Forecast                                         │
│  Mon  Tue  Wed  Thu  Fri                               │
│  ☀️   🌤️   🌧️   ☀️   ☀️                               │
│  18°  20°  15°  22°  25°                               │
│  12°  14°  10°  16°  18°                               │
├─────────────────────────────────────────────────────────┤
│  Next 12 Hours                                          │
│  12:00 15:00 18:00 21:00 00:00 03:00 06:00 09:00       │
│   ☀️    🌤️    🌧️    🌧️    🌧️    ☀️    ☀️    ☀️        │
│   22°   20°   18°   16°   14°   12°   15°   18°       │
└─────────────────────────────────────────────────────────┘
```

## Technical Details

### Browser Automation
- Uses Playwright for headless Chrome rendering
- Captures screenshots at exact display resolution (800x480)
- Optimized browser flags for performance
- Automatic font loading and rendering

### Fallback System
If Playwright is not available or fails:
1. Falls back to basic HTML generation
2. Uses PIL for simple text-based rendering
3. Maintains functionality without browser dependency

### Color Optimization
- CSS designed with e-ink 6-color palette in mind
- High contrast colors for better readability
- Temperature-based color coding
- Weather condition color mapping

### Performance
- Template caching for faster rendering
- Browser instance reuse
- Optimized CSS for minimal rendering time
- Efficient image capture and processing

## Comparison with Standard Weather Mode

| Feature | Standard Weather | HTML Weather |
|---------|------------------|--------------|
| **Design** | Basic PIL drawing | Modern HTML/CSS |
| **Typography** | System fonts | Inter font family |
| **Icons** | Simple geometric shapes | Professional weather icons |
| **Layout** | Manual positioning | CSS Grid/Flexbox |
| **Colors** | Basic 6-color palette | Enhanced color schemes |
| **Maintenance** | Complex PIL code | Easy CSS modifications |
| **Performance** | Fast | Slightly slower (browser overhead) |
| **Dependencies** | Minimal | Playwright + Jinja2 |

## Troubleshooting

### Common Issues

1. **Playwright not installed**
   - Install: `pip install playwright`
   - Install browsers: `playwright install chromium`

2. **Browser rendering fails**
   - Check system dependencies
   - Verify display resolution settings
   - Check browser flags in code

3. **Font loading issues**
   - Fonts are inlined in HTML for reliability
   - Fallback fonts specified in CSS

4. **Performance issues**
   - Browser startup adds overhead
   - Consider increasing `display_time` in config
   - Monitor system resources

### Debug Mode
Enable debug logging to troubleshoot issues:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

- **Animation Support**: CSS animations for weather transitions
- **More Data**: Additional weather metrics (UV index, pressure, etc.)
- **Custom Themes**: Multiple color schemes and layouts
- **Weather Alerts**: Severe weather warnings and alerts
- **Location Services**: Automatic location detection
- **Historical Data**: Weather trends and comparisons

## Contributing

To modify the weather display:

1. **Layout Changes**: Edit `templates/weather.css`
2. **Content Changes**: Edit `templates/weather.html`
3. **Logic Changes**: Edit `modules/weather_html.py`
4. **Test Changes**: Run `test_weather_html.py`

The modular design makes it easy to customize the appearance and functionality of the weather display.

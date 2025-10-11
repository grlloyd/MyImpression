# Custom Weather Icons

This directory contains custom weather icons for the e-ink display. The system supports multiple icon sources with automatic fallbacks.

## Icon Sources (in order of preference)

1. **Custom Icons** - Your own PNG files optimized for e-ink
2. **Font Awesome** - Vector icons (fallback)
3. **Emoji** - Unicode emoji (final fallback)

## Required Custom Icons

Place these PNG files in this directory for custom icons:

- `clear.png` - Clear/sunny weather
- `partly_cloudy.png` - Partly cloudy
- `overcast.png` - Overcast/cloudy
- `fog.png` - Fog/mist
- `drizzle.png` - Light rain/drizzle
- `rain.png` - Rain
- `snow.png` - Snow
- `showers.png` - Rain showers
- `snow_showers.png` - Snow showers
- `thunderstorm.png` - Thunderstorms

## Icon Specifications

For best results on e-ink displays:

- **Format**: PNG with transparency
- **Size**: 64x64 pixels (will be scaled as needed)
- **Style**: High contrast, simple designs
- **Colors**: Black/white or very limited color palette
- **Background**: Transparent

## Example Icon Styles

Good e-ink icons should be:
- Simple, bold designs
- High contrast
- Minimal details
- Clear at small sizes

## Configuration

The icon system is configured in `icon_config.json`. You can:
- Change the order of icon sources
- Add new weather conditions
- Modify fallback behavior

## Testing

Use the test files to preview your custom icons:
- `weather_test_updated.html` - Browser preview
- `test_weather_html.py` - Generate screenshot

## Fallback Behavior

If custom icons are not found, the system will:
1. Try Font Awesome icons
2. Fall back to emoji
3. Show a question mark (❓) for unknown conditions

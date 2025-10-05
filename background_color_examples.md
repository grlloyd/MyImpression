# Background Color Configuration

The `background_color` setting in `config.json` controls the color of the bars that appear when images don't fill the entire 800x480 display.

## Configuration Options

### Named Colors
```json
{
  "photo_cycle": {
    "background_color": "white"        // Default
    "background_color": "black"
    "background_color": "gray"
    "background_color": "light_gray"
    "background_color": "dark_gray"
  }
}
```

### Custom RGB Colors
```json
{
  "photo_cycle": {
    "background_color": [255, 255, 255]  // White
    "background_color": [0, 0, 0]        // Black
    "background_color": [128, 128, 128]   // Gray
    "background_color": [192, 192, 192]   // Light gray
    "background_color": [64, 64, 64]     // Dark gray
    "background_color": [240, 240, 240]  // Off-white
    "background_color": [50, 50, 50]      // Very dark gray
  }
}
```

## Examples

### White Background (Default)
```json
{
  "photo_cycle": {
    "background_color": "white"
  }
}
```
- Good for: Most photos, clean look
- Best for: Photos with white/light content

### Black Background
```json
{
  "photo_cycle": {
    "background_color": "black"
  }
}
```
- Good for: Dark photos, dramatic effect
- Best for: Photos with dark content

### Custom Color
```json
{
  "photo_cycle": {
    "background_color": [240, 240, 240]
  }
}
```
- Good for: Subtle off-white that's easier on the eyes
- Best for: Long viewing sessions

## When Background Color Shows

The background color appears when:
- **Wide photos (16:9)**: Bars appear top and bottom
- **Tall photos (3:4)**: Bars appear left and right
- **Square photos (1:1)**: Bars appear left and right
- **Small photos**: When enlarged, may not fill entire display

## Tips

1. **Match your photos**: Choose a background that complements your photo collection
2. **Consider viewing environment**: Dark backgrounds for dark rooms, light for bright rooms
3. **Test different colors**: Try a few options to see what looks best with your photos
4. **RGB values**: Use online color pickers to find exact RGB values you want

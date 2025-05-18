# Project Notes and References

## Mouse Functions (Potential Library Features)

These are functions that could potentially be developed into a standalone mouse control library.

-   `move_cursor(x, y)` - Move the mouse pointer to the specified coordinates.
-   `get_cursor_position()` - Return the current position of the mouse pointer.
-   `click(button='left', x=None, y=None, clicks=1, interval=0)` - Perform a mouse click (left, right, or middle) at the current or specified position.
-   `double_click(button='left', x=None, y=None)` - Perform a double-click.
-   `right_click(x=None, y=None)` - Shortcut for a right-click.
-   `middle_click(x=None, y=None)` - Shortcut for a middle-click.
-   `press_button(button='left', x=None, y=None)` - Press and hold a mouse button down.
-   `release_button(button='left', x=None, y=None)` - Release a mouse button.
-   `drag_to(x, y, duration=0)` - Drag the mouse to a specific position.
-   `drag_by(dx, dy, duration=0)` - Drag the mouse by a relative amount.
-   `scroll(vertical=0, horizontal=0)` - Scroll vertically or horizontally.
-   `hover(x, y)` - Move the mouse to a position and pause to simulate a hover.
-   `select_area(x1, y1, x2, y2)` - Select a rectangular area (for selection or drag operations).

## Common Screen Resolutions (Reference)

A list of common screen resolutions for reference purposes.

| Label           | Resolution  | Aspect Ratio (Approx) |
|-----------------|-------------|-----------------------|
| SD (Standard)   | 640 x 480   | 4:3                   |
| HD              | 1280 x 720  | 16:9                  |
| WXGA            | 1366 x 768  | 16:9                  |
| Full HD (FHD)   | 1920 x 1080 | 16:9                  |
| WUXGA           | 1920 x 1200 | 16:10                 |
| QHD/2K          | 2560 x 1440 | 16:9                  |
| WQXGA           | 2560 x 1600 | 16:10                 |
| 4K UHD          | 3840 x 2160 | 16:9                  |
| 8K UHD          | 7680 x 4320 | 16:9                  |

## Ideal Perlin Mouse Simulator Configuration

This represents a preferred configuration for the Perlin Mouse Simulator application.

```python
# Ideal Configuration Values
config = {
    "win_h": 1560,         # Window width
    "win_w": 2560,         # Window height 
    "noise_scale": 100.0,  # Scale of the Perlin noise
    "res_scale": 1.0,      # Resolution scale for the noise map (1.0 = full resolution)
    "speed_min": 20.0,     # Minimum pixels moved per step
    "speed_max_mul": 2.0,  # Multiplier for additional speed from noise
    "jitter_mul": 20.0,    # Multiplier for random jitter strength
    "dev_deg": 35.0,       # Maximum angular deviation (in degrees)
    "sleep": 0.03          # Sleep time (in seconds) between steps
}
```

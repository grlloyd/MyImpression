"""
Button Handler Module
Handles GPIO button input for mode switching with LED feedback.
"""

import threading
import time
import logging
from typing import Callable, Optional

try:
    import gpiod
    import gpiodevice
    from gpiod.line import Bias, Direction, Edge, Value
    GPIO_AVAILABLE = True
except ImportError:
    GPIO_AVAILABLE = False


class ButtonHandler:
    """Handles GPIO button input for the Inky Impression."""
    
    def __init__(self, config: dict, callback: Callable[[str], None]):
        """Initialize button handler with configuration and callback."""
        self.config = config
        self.callback = callback
        self.running = False
        self.thread = None
        self.logger = logging.getLogger(__name__)
        
        if not GPIO_AVAILABLE:
            self.logger.warning("GPIO not available - button handling disabled")
            return
        
        # GPIO pins for each button (from top to bottom)
        # These correspond to buttons A, B, C and D respectively
        self.BUTTONS = [5, 6, 16, 24]
        self.LABELS = ["A", "B", "C", "D"]
        
        # LED pin (GPIO 13 for Inky Impression)
        self.LED_PIN = 13
        
        # Create settings for all the input pins
        self.INPUT = gpiod.LineSettings(
            direction=Direction.INPUT, 
            bias=Bias.PULL_UP, 
            edge_detection=Edge.FALLING
        )
        
        # Create settings for LED output
        self.LED_OUTPUT = gpiod.LineSettings(
            direction=Direction.OUTPUT,
            bias=Bias.DISABLED
        )
        
        try:
            # Find the gpiochip device
            self.chip = gpiodevice.find_chip_by_platform()
            
            # Build config for each pin/line
            self.OFFSETS = [self.chip.line_offset_from_id(id) for id in self.BUTTONS]
            line_config = dict.fromkeys(self.OFFSETS, self.INPUT)
            
            # Add LED to the line config
            led_offset = self.chip.line_offset_from_id(self.LED_PIN)
            line_config[led_offset] = self.LED_OUTPUT
            
            # Request the lines
            self.request = self.chip.request_lines(
                consumer="myimpression-buttons", 
                config=line_config
            )
            
            # Store LED offset for easy access
            self.led_offset = led_offset
            
            # Initialize LED as off
            self.request.set_value(self.led_offset, Value.INACTIVE)
            
            self.logger.info("Button handler with LED initialized successfully")
            
        except Exception as e:
            self.logger.error(f"Failed to initialize button handler: {e}")
            self.chip = None
            self.request = None
            self.led_offset = None
    
    def start(self):
        """Start button monitoring in a separate thread."""
        if not GPIO_AVAILABLE or not self.chip or not self.request:
            self.logger.warning("Button handler not available")
            return
        
        self.running = True
        self.thread = threading.Thread(target=self._monitor_buttons, daemon=True)
        self.thread.start()
        self.logger.info("Button monitoring started")
    
    def stop(self):
        """Stop button monitoring."""
        self.running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=2)
        self.logger.info("Button monitoring stopped")
    
    def _flash_led(self, duration: float = 0.2):
        """Flash the LED for the specified duration."""
        if not self.request or not self.led_offset:
            return
        
        try:
            # Turn LED on
            self.request.set_value(self.led_offset, Value.ACTIVE)
            time.sleep(duration)
            # Turn LED off
            self.request.set_value(self.led_offset, Value.INACTIVE)
        except Exception as e:
            self.logger.error(f"Error controlling LED: {e}")
    
    def _monitor_buttons(self):
        """Monitor button presses in a loop."""
        while self.running:
            try:
                for event in self.request.read_edge_events():
                    if not self.running:
                        break
                    
                    # Find which button was pressed
                    index = self.OFFSETS.index(event.line_offset)
                    gpio_number = self.BUTTONS[index]
                    label = self.LABELS[index]
                    
                    self.logger.info(f"Button {label} pressed (GPIO #{gpio_number})")
                    
                    # Flash LED to indicate button press
                    self._flash_led(0.3)  # Flash for 300ms
                    
                    # Call the callback function
                    if self.callback:
                        self.callback(label)
                        
            except Exception as e:
                self.logger.error(f"Error monitoring buttons: {e}")
                time.sleep(0.1)
    
    def simulate_button_press(self, button: str):
        """Simulate a button press for testing."""
        if button in self.LABELS:
            self.logger.info(f"Simulating button press: {button}")
            if self.callback:
                self.callback(button)
        else:
            self.logger.warning(f"Invalid button label: {button}")

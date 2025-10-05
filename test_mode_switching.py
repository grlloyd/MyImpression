#!/usr/bin/env python3
"""
Test script for mode switching functionality.
This script tests that modes properly stop when switching to a new mode.
"""

import time
import threading
from unittest.mock import Mock, MagicMock


class MockMode:
    """Mock mode for testing."""
    
    def __init__(self, name):
        self.name = name
        self.running = False
        self.start_time = None
        self.stop_time = None
    
    def run(self, running_flag):
        """Mock run method that tracks when it starts and stops."""
        self.running = True
        self.start_time = time.time()
        print(f"Mode {self.name} started")
        
        # Simulate work
        while running_flag():
            time.sleep(0.1)
        
        self.running = False
        self.stop_time = time.time()
        print(f"Mode {self.name} stopped (ran for {self.stop_time - self.start_time:.1f}s)")


def test_mode_switching():
    """Test that modes properly stop when switching."""
    print("Testing mode switching...")
    
    # Create mock modes
    modes = {
        "photo_cycle": MockMode("photo_cycle"),
        "weather": MockMode("weather"),
        "solar_monitor": MockMode("solar_monitor"),
        "news_feed": MockMode("news_feed")
    }
    
    # Simulate the app's mode switching logic
    current_mode = None
    mode_thread = None
    mode_running = False
    
    def switch_mode(mode_name):
        nonlocal current_mode, mode_thread, mode_running
        
        # Stop current mode
        if current_mode and mode_thread and mode_thread.is_alive():
            print(f"Stopping current mode: {current_mode}")
            mode_running = False
            mode_thread.join(timeout=2)
        
        # Start new mode
        current_mode = mode_name
        mode_running = True
        
        def should_continue():
            return mode_running
        
        mode_thread = threading.Thread(
            target=modes[mode_name].run,
            args=(should_continue,),
            daemon=True
        )
        mode_thread.start()
        print(f"Started mode: {mode_name}")
    
    # Test switching between modes
    print("\n=== Test 1: Switch from photo_cycle to weather ===")
    switch_mode("photo_cycle")
    time.sleep(1)  # Let it run for a bit
    switch_mode("weather")
    time.sleep(1)
    
    print(f"Photo cycle running: {modes['photo_cycle'].running}")
    print(f"Weather running: {modes['weather'].running}")
    
    print("\n=== Test 2: Switch from weather to solar_monitor ===")
    switch_mode("solar_monitor")
    time.sleep(1)
    
    print(f"Weather running: {modes['weather'].running}")
    print(f"Solar monitor running: {modes['solar_monitor'].running}")
    
    print("\n=== Test 3: Switch from solar_monitor to news_feed ===")
    switch_mode("news_feed")
    time.sleep(1)
    
    print(f"Solar monitor running: {modes['solar_monitor'].running}")
    print(f"News feed running: {modes['news_feed'].running}")
    
    # Stop all modes
    mode_running = False
    if mode_thread and mode_thread.is_alive():
        mode_thread.join(timeout=2)
    
    print(f"\nFinal state:")
    for name, mode in modes.items():
        print(f"  {name}: running={mode.running}, duration={mode.stop_time - mode.start_time if mode.stop_time else 'N/A':.1f}s")


if __name__ == "__main__":
    test_mode_switching()

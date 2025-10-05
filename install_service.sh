#!/bin/bash
# MyImpression Service Installation Script
# Installs MyImpression as a systemd service

echo "MyImpression Service Installation"
echo "================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

# Get the current directory
CURRENT_DIR=$(pwd)
SERVICE_DIR="/home/pi/MyImpression"

echo "Installing MyImpression service..."

# Copy service file
cp myimpression.service /etc/systemd/system/

# Update service file with correct paths
sed -i "s|/home/pi/MyImpression|$SERVICE_DIR|g" /etc/systemd/system/myimpression.service

# Reload systemd
systemctl daemon-reload

# Enable the service
systemctl enable myimpression.service

echo ""
echo "Service installed successfully!"
echo ""
echo "Commands:"
echo "  Start service:    sudo systemctl start myimpression"
echo "  Stop service:     sudo systemctl stop myimpression"
echo "  Restart service:  sudo systemctl restart myimpression"
echo "  Check status:     sudo systemctl status myimpression"
echo "  View logs:        sudo journalctl -u myimpression -f"
echo ""
echo "The service will start automatically on boot."

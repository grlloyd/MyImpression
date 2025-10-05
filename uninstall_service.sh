#!/bin/bash
# MyImpression Service Uninstallation Script

echo "MyImpression Service Uninstallation"
echo "==================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    echo "Please run as root (use sudo)"
    exit 1
fi

echo "Stopping and disabling MyImpression service..."

# Stop the service
systemctl stop myimpression.service

# Disable the service
systemctl disable myimpression.service

# Remove the service file
rm -f /etc/systemd/system/myimpression.service

# Reload systemd
systemctl daemon-reload

echo "Service uninstalled successfully!"
echo "MyImpression will no longer start automatically on boot."

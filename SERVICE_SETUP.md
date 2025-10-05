# MyImpression Service Setup

This guide shows how to install MyImpression as a systemd service that runs automatically on boot.

## Installation

### 1. Install the Service
```bash
sudo chmod +x install_service.sh
sudo ./install_service.sh
```

### 2. Start the Service
```bash
sudo systemctl start myimpression
```

### 3. Check Status
```bash
sudo systemctl status myimpression
```

## Service Management

### Start/Stop/Restart
```bash
# Start the service
sudo systemctl start myimpression

# Stop the service
sudo systemctl stop myimpression

# Restart the service
sudo systemctl restart myimpression
```

### Check Status
```bash
# Check if service is running
sudo systemctl status myimpression

# View live logs
sudo journalctl -u myimpression -f

# View recent logs
sudo journalctl -u myimpression --since "1 hour ago"
```

### Enable/Disable Auto-Start
```bash
# Enable auto-start on boot
sudo systemctl enable myimpression

# Disable auto-start on boot
sudo systemctl disable myimpression
```

## Uninstallation

To remove the service:
```bash
sudo chmod +x uninstall_service.sh
sudo ./uninstall_service.sh
```

## Troubleshooting

### Service Won't Start
1. Check the logs:
   ```bash
   sudo journalctl -u myimpression -f
   ```

2. Verify the virtual environment exists:
   ```bash
   ls -la /home/pi/MyImpression/venv/
   ```

3. Test manual run:
   ```bash
   cd /home/pi/MyImpression
   source venv/bin/activate
   python main.py
   ```

### GPIO Permission Issues
If buttons don't work, ensure the user is in the gpio group:
```bash
sudo usermod -a -G gpio pi
```

### Display Not Found
1. Check if the display is detected:
   ```bash
   sudo dmesg | grep -i inky
   ```

2. Verify the Inky library is installed:
   ```bash
   /home/pi/MyImpression/venv/bin/python -c "import inky; print('Inky library OK')"
   ```

## Service Configuration

The service runs as user `pi` with:
- Working directory: `/home/pi/MyImpression`
- Virtual environment: `/home/pi/MyImpression/venv`
- Auto-restart on failure
- GPIO group access for buttons

## Manual vs Service Mode

- **Manual mode**: Run `./run.sh` for testing
- **Service mode**: Runs automatically on boot, managed by systemd

You can switch between modes anytime:
- Stop service: `sudo systemctl stop myimpression`
- Run manually: `./run.sh`
- Start service: `sudo systemctl start myimpression`

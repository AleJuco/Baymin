# USB Web Server Setup Guide

## What This Does
When you plug the Raspberry Pi into a computer via USB, it automatically:
1. Detects the USB connection
2. Starts the Flask webapp (webapp.py)
3. Makes it accessible from the connected computer

## Usage

### Option 1: Run Once (Manual Start)
Start the webapp immediately:
```bash
cd /home/baymini/Baymin/Functions
source /home/baymini/Baymin/venv/bin/activate
python USBWebServer.py
```

### Option 2: Monitor Mode (Auto-Start on USB)
Monitor for USB connections and auto-start webapp:
```bash
cd /home/baymini/Baymin/Functions
source /home/baymini/Baymin/venv/bin/activate
python USBWebServer.py --monitor
```

### Custom Port
Run on a different port:
```bash
python USBWebServer.py --port 8080
```

## Accessing from Connected Computer

Once running, access the webapp at:
- `http://<pi-ip-address>:5000` (replace with actual IP)
- `http://raspberrypi.local:5000` (if mDNS/Bonjour works)
- `http://localhost:5000` (if USB networking is configured)

## Auto-Start on Boot (Optional)

To automatically run this when the Pi boots:

### Method 1: Systemd Service
1. Create service file:
```bash
sudo nano /etc/systemd/system/usb-webapp.service
```

2. Add this content:
```ini
[Unit]
Description=USB Web Server Auto-Start
After=network.target

[Service]
Type=simple
User=baymini
WorkingDirectory=/home/baymini/Baymin/Functions
ExecStart=/home/baymini/Baymin/venv/bin/python /home/baymini/Baymin/Functions/USBWebServer.py --monitor
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

3. Enable and start:
```bash
sudo systemctl enable usb-webapp.service
sudo systemctl start usb-webapp.service
```

4. Check status:
```bash
sudo systemctl status usb-webapp.service
```

### Method 2: Add to rc.local
```bash
sudo nano /etc/rc.local
```

Add before `exit 0`:
```bash
su - baymini -c "cd /home/baymini/Baymin/Functions && /home/baymini/Baymin/venv/bin/python USBWebServer.py --monitor &"
```

## USB Gadget Mode Setup (For Direct PC Connection)

To enable USB ethernet gadget mode on Raspberry Pi:

1. Edit config.txt:
```bash
sudo nano /boot/firmware/config.txt
```

Add at the end:
```
dtoverlay=dwc2
```

2. Edit cmdline.txt:
```bash
sudo nano /boot/firmware/cmdline.txt
```

Add `modules-load=dwc2,g_ether` after `rootwait`

3. Reboot:
```bash
sudo reboot
```

Now when you connect Pi to PC via USB, it will appear as a network device.

## Troubleshooting

### Webapp not accessible from PC
- Check if Pi has an IP address: `ip addr show usb0`
- Ping the Pi from your PC
- Check firewall settings
- Try `http://raspberrypi.local:5000`

### Monitor mode not detecting USB
- Run `lsmod | grep usb` to check USB modules
- Run `ip link show` to see network interfaces
- Try manual start mode first to test webapp

### Port already in use
- Stop any running Flask instances: `pkill -f webapp.py`
- Use a different port: `--port 8080`

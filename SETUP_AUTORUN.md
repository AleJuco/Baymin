# Baymin Auto-Run Setup Guide

This guide covers:
1. Testing the webapp without USB gadget mode
2. Configuring USB gadget mode (OTG) for Pi Zero/4
3. Setting up auto-run on boot
4. Troubleshooting

---

## Quick Testing (Without USB Gadget Setup)

### Test webapp locally:
```bash
cd /home/baymini/Baymin
source venv/bin/activate
python webapp.py
```
Access at: http://localhost:5000

### Test USBWebServer in single-run mode:
```bash
cd /home/baymini/Baymin/Functions
source ../venv/bin/activate
python USBWebServer.py
```

---

## USB Gadget Mode Setup (Pi Zero/4 Only)

⚠️ **Note**: USB gadget mode only works on:
- Raspberry Pi Zero / Zero W / Zero 2 W
- Raspberry Pi 4 (with USB-C data cable)
- NOT supported on Pi 3

### Step 1: Enable USB Gadget Mode

1. Edit `/boot/config.txt`:
```bash
sudo nano /boot/config.txt
```

Add at the end:
```
dtoverlay=dwc2
```

2. Edit `/boot/cmdline.txt`:
```bash
sudo nano /boot/cmdline.txt
```

Add `modules-load=dwc2,g_ether` after `rootwait`:
```
... rootwait modules-load=dwc2,g_ether quiet ...
```
(Keep everything on ONE line)

3. Create network configuration:
```bash
sudo nano /etc/network/interfaces.d/usb0
```

Add:
```
auto usb0
allow-hotplug usb0
iface usb0 inet static
    address 192.168.7.2
    netmask 255.255.255.0
```

4. Reboot:
```bash
sudo reboot
```

### Step 2: Configure Host PC

#### On Windows:
1. Install RNDIS driver (usually automatic)
2. Go to Network Connections
3. Find "USB Ethernet/RNDIS Gadget"
4. Set IP to: `192.168.7.1`, Subnet: `255.255.255.0`

#### On macOS:
1. Go to System Preferences → Network
2. Find "RNDIS/Ethernet Gadget"
3. Configure IPv4: Manual
4. IP: `192.168.7.1`, Subnet: `255.255.255.0`

#### On Linux:
```bash
sudo ip addr add 192.168.7.1/24 dev usb0
```

### Step 3: Test Connection

From host PC:
```bash
ping 192.168.7.2
ssh baymini@192.168.7.2
```

Access webapp at: `http://192.168.7.2:5000`

---

## Auto-Run on Boot (Systemd Service)

### Option 1: Auto-Run Webapp on Boot

Create systemd service:
```bash
sudo nano /etc/systemd/system/baymin-webapp.service
```

Add:
```ini
[Unit]
Description=Baymin Flask Webapp
After=network.target

[Service]
Type=simple
User=baymini
WorkingDirectory=/home/baymini/Baymin
Environment="PATH=/home/baymini/Baymin/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/baymini/Baymin/venv/bin/python /home/baymini/Baymin/webapp.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable baymin-webapp.service
sudo systemctl start baymin-webapp.service
```

Check status:
```bash
sudo systemctl status baymin-webapp.service
```

View logs:
```bash
sudo journalctl -u baymin-webapp.service -f
```

### Option 2: Auto-Run Wake Word Detection on Boot

Create service:
```bash
sudo nano /etc/systemd/system/baymin-wake.service
```

Add:
```ini
[Unit]
Description=Baymin Wake Word Detection
After=sound.target network.target graphical.target
Wants=graphical.target

[Service]
Type=simple
User=baymini
WorkingDirectory=/home/baymini/Baymin/Functions
Environment="PATH=/home/baymini/Baymin/venv/bin:/usr/local/bin:/usr/bin:/bin"
Environment="DISPLAY=:0"
Environment="GEMINI_API_KEY=your-api-key-here"
ExecStart=/home/baymini/Baymin/venv/bin/python /home/baymini/Baymin/Functions/Wake.py
Restart=always
RestartSec=10

[Install]
WantedBy=graphical.target
```

⚠️ **Important**: Replace `your-api-key-here` with your actual Gemini API key!

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable baymin-wake.service
sudo systemctl start baymin-wake.service
```

### Option 3: USB Monitor Mode (Auto-start webapp on USB plug)

Create service:
```bash
sudo nano /etc/systemd/system/baymin-usb.service
```

Add:
```ini
[Unit]
Description=Baymin USB Web Server Monitor
After=network.target

[Service]
Type=simple
User=baymini
WorkingDirectory=/home/baymini/Baymin/Functions
Environment="PATH=/home/baymini/Baymin/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/baymini/Baymin/venv/bin/python /home/baymini/Baymin/Functions/USBWebServer.py --monitor
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable:
```bash
sudo systemctl daemon-reload
sudo systemctl enable baymin-usb.service
sudo systemctl start baymin-usb.service
```

---

## Testing Without USB Gadget Mode

If you don't have USB gadget hardware or just want to test:

### Method 1: Test on Pi with Browser
```bash
# On Pi terminal:
cd /home/baymini/Baymin
source venv/bin/activate
python webapp.py

# Open browser on Pi (if GUI installed):
chromium-browser http://localhost:5000
```

### Method 2: Test over WiFi/Ethernet

1. Get Pi's IP address:
```bash
hostname -I
```

2. Start webapp:
```bash
cd /home/baymini/Baymin
source venv/bin/activate
python webapp.py
```

3. From another device on same network:
```
http://[PI_IP_ADDRESS]:5000
```

### Method 3: SSH Port Forwarding

From your PC:
```bash
ssh -L 5000:localhost:5000 baymini@[PI_IP]
```

Then open `http://localhost:5000` on your PC

---

## Complete Auto-Start Everything

To start all Baymin services on boot:

```bash
# Enable all services
sudo systemctl enable baymin-webapp.service
sudo systemctl enable baymin-wake.service

# Start them now
sudo systemctl start baymin-webapp.service
sudo systemctl start baymin-wake.service

# Check status
sudo systemctl status baymin-webapp.service
sudo systemctl status baymin-wake.service
```

---

## Useful Commands

### Check if services are running:
```bash
sudo systemctl status baymin-*
```

### Stop a service:
```bash
sudo systemctl stop baymin-webapp.service
```

### Restart a service:
```bash
sudo systemctl restart baymin-webapp.service
```

### View live logs:
```bash
# Webapp logs
sudo journalctl -u baymin-webapp.service -f

# Wake word logs
sudo journalctl -u baymin-wake.service -f
```

### Disable auto-start:
```bash
sudo systemctl disable baymin-webapp.service
```

---

## Troubleshooting

### Webapp won't start:
```bash
# Check if port 5000 is in use
sudo netstat -tulpn | grep 5000

# Kill process on port 5000
sudo kill $(sudo lsof -t -i:5000)
```

### Wake word service fails:
```bash
# Check display
echo $DISPLAY  # Should be :0

# Check camera permissions
ls -l /dev/video*

# Check microphone
arecord -l
```

### USB gadget not working:
```bash
# Check if modules loaded
lsmod | grep dwc2

# Check USB interface
ip addr show usb0

# Manual load
sudo modprobe dwc2
sudo modprobe g_ether
```

### Permission errors:
```bash
# Add user to required groups
sudo usermod -a -G audio,video,dialout baymini

# Reboot required
sudo reboot
```

---

## Environment Variables

Set Gemini API key persistently:

```bash
# Add to ~/.bashrc
echo 'export GEMINI_API_KEY="your-api-key-here"' >> ~/.bashrc
source ~/.bashrc

# Verify
echo $GEMINI_API_KEY
```

For systemd services, add to the service file:
```ini
Environment="GEMINI_API_KEY=your-key"
```

---

## Security Notes

1. **Never commit API keys to Git**
2. **Use environment variables** for secrets
3. **Change default Flask secret key** in webapp.py
4. **Restrict webapp access** if on public network
5. **Use HTTPS** for production (setup nginx reverse proxy)

---

## Quick Start Summary

### Minimal setup (no auto-start):
```bash
cd /home/baymini/Baymin
source venv/bin/activate

# Terminal 1: Run webapp
python webapp.py

# Terminal 2: Run wake word detection
cd Functions
export DISPLAY=:0
python Wake.py
```

### Auto-start on boot:
```bash
# Create both service files (see above)
sudo systemctl daemon-reload
sudo systemctl enable baymin-webapp.service baymin-wake.service
sudo systemctl start baymin-webapp.service baymin-wake.service
```

---

Happy building! 🤖

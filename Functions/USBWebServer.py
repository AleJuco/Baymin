"""
USB Web Server Auto-Start
Detects USB connection and starts webapp.py
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import subprocess
import time
import socket
import webbrowser
from threading import Thread

class USBWebServer:
    def __init__(self, webapp_path="../webapp.py", port=5000):
        """
        Initialize USB web server manager.
        
        Args:
            webapp_path (str): Path to webapp.py
            port (int): Port to run Flask on
        """
        self.webapp_path = os.path.join(
            os.path.dirname(__file__),
            webapp_path
        )
        self.port = port
        self.process = None
        
    def get_usb_ip(self):
        """Get the IP address of the USB network interface."""
        try:
            # Common USB gadget interface names
            interfaces = ['usb0', 'usb1', 'eth0', 'eth1']
            
            for interface in interfaces:
                result = subprocess.run(
                    ['ip', 'addr', 'show', interface],
                    capture_output=True,
                    text=True
                )
                
                if result.returncode == 0:
                    # Parse IP address from output
                    for line in result.stdout.split('\n'):
                        if 'inet ' in line:
                            ip = line.split()[1].split('/')[0]
                            print(f"Found USB interface {interface} with IP: {ip}")
                            return ip
            
            # Fallback to localhost
            return '127.0.0.1'
            
        except Exception as e:
            print(f"Error getting USB IP: {e}")
            return '127.0.0.1'
    
    def is_usb_connected(self):
        """Check if USB connection is active."""
        try:
            # Check for USB gadget mode
            result = subprocess.run(
                ['lsmod'],
                capture_output=True,
                text=True
            )
            
            # Check if USB gadget modules are loaded
            if 'g_ether' in result.stdout or 'usb_f_ecm' in result.stdout:
                return True
            
            # Alternative: check if usb0 interface exists
            result = subprocess.run(
                ['ip', 'link', 'show', 'usb0'],
                capture_output=True,
                text=True
            )
            
            return result.returncode == 0
            
        except Exception as e:
            print(f"Error checking USB connection: {e}")
            return False
    
    def start_webapp(self):
        """Start the Flask webapp."""
        if self.process:
            print("Webapp already running")
            return
        
        print(f"\n{'='*60}")
        print("🚀 Starting Flask webapp...")
        print(f"   Path: {self.webapp_path}")
        print(f"   Port: {self.port}")
        print("="*60)
        
        try:
            # Get the virtual environment python
            venv_python = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'venv', 'bin', 'python'
            )
            
            if not os.path.exists(venv_python):
                venv_python = 'python3'
            
            # Start webapp process
            self.process = subprocess.Popen(
                [venv_python, self.webapp_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for server to start
            time.sleep(2)
            
            # Check if process is running
            if self.process.poll() is None:
                ip = self.get_usb_ip()
                url = f"http://{ip}:{self.port}"
                
                print(f"\n✅ Webapp started successfully!")
                print(f"📱 Access at: {url}")
                print(f"🔗 Or try: http://localhost:{self.port}")
                
                # Try to open browser (works if connected PC has access)
                try:
                    webbrowser.open(url)
                    print("🌐 Opened browser automatically")
                except:
                    print("⚠️ Could not open browser automatically")
                    print(f"   Please open: {url}")
                
                return True
            else:
                print("❌ Webapp failed to start")
                return False
                
        except Exception as e:
            print(f"Error starting webapp: {e}")
            return False
    
    def stop_webapp(self):
        """Stop the Flask webapp."""
        if self.process:
            print("\n🛑 Stopping webapp...")
            self.process.terminate()
            self.process.wait(timeout=5)
            self.process = None
            print("✓ Webapp stopped")
    
    def monitor_usb_connection(self):
        """Monitor USB connection and manage webapp."""
        print("\n{'='*60}")
        print("📡 Monitoring USB connection...")
        print("   Plug Pi into computer via USB to start webapp")
        print("   Press Ctrl+C to stop")
        print("="*60)
        
        was_connected = False
        
        try:
            while True:
                is_connected = self.is_usb_connected()
                
                if is_connected and not was_connected:
                    print("\n🔌 USB connected!")
                    self.start_webapp()
                    was_connected = True
                    
                elif not is_connected and was_connected:
                    print("\n🔌 USB disconnected!")
                    self.stop_webapp()
                    was_connected = False
                
                time.sleep(2)  # Check every 2 seconds
                
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping USB monitor...")
            if self.process:
                self.stop_webapp()
    
    def run_once(self):
        """Start webapp immediately without monitoring."""
        print("\n{'='*60}")
        print("🚀 USB Web Server - Single Run Mode")
        print("="*60)
        
        if self.start_webapp():
            print("\n✓ Server running. Press Ctrl+C to stop")
            try:
                # Keep running until interrupted
                self.process.wait()
            except KeyboardInterrupt:
                print("\n\n🛑 Stopping server...")
                self.stop_webapp()


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='USB Web Server Manager')
    parser.add_argument('--monitor', action='store_true', 
                       help='Monitor USB connection and auto-start webapp')
    parser.add_argument('--port', type=int, default=5000,
                       help='Port to run webapp on (default: 5000)')
    
    args = parser.parse_args()
    
    server = USBWebServer(port=args.port)
    
    if args.monitor:
        # Monitor mode - auto-start on USB connection
        server.monitor_usb_connection()
    else:
        # Single run mode - start immediately
        server.run_once()


if __name__ == "__main__":
    main()

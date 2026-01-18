import subprocess
import os
import time
import re
from pathlib import Path

class Speaker:
    def __init__(self, speaker_mac_address=None):
        """
        Initialize the Speaker class for audio playback via Bluetooth speaker.
        
        Args:
            speaker_mac_address (str): MAC address of the Bluetooth speaker (e.g., "AA:BB:CC:DD:EE:FF")
                                      If None, you'll need to connect manually or use connect_bluetooth()
        """
        self.current_process = None
        self.speaker_mac = speaker_mac_address
        
    def scan_bluetooth_devices(self, scan_time=10):
        """
        Scan for nearby Bluetooth devices.
        
        Args:
            scan_time (int): Time to scan in seconds
            
        Returns:
            list: List of dictionaries with device info (name, mac_address)
        """
        print(f"Scanning for Bluetooth devices for {scan_time} seconds...")
        devices = []
        
        try:
            # Start scanning
            subprocess.run(['bluetoothctl', 'scan', 'on'], timeout=1, capture_output=True)
            time.sleep(scan_time)
            subprocess.run(['bluetoothctl', 'scan', 'off'], timeout=1, capture_output=True)
            
            # Get list of devices
            result = subprocess.run(['bluetoothctl', 'devices'], capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if line.startswith('Device'):
                    parts = line.split(' ', 2)
                    if len(parts) >= 3:
                        mac = parts[1]
                        name = parts[2] if len(parts) > 2 else "Unknown"
                        devices.append({'mac': mac, 'name': name})
                        print(f"Found: {name} ({mac})")
            
            return devices
            
        except Exception as e:
            print(f"Error scanning for devices: {e}")
            return []
    
    def pair_bluetooth_device(self, mac_address):
        """
        Pair with a Bluetooth device.
        
        Args:
            mac_address (str): MAC address of the device
            
        Returns:
            bool: True if successful
        """
        try:
            print(f"Pairing with {mac_address}...")
            result = subprocess.run(['bluetoothctl', 'pair', mac_address], 
                                  capture_output=True, text=True, timeout=30)
            
            if "Pairing successful" in result.stdout or "already paired" in result.stdout:
                print("Pairing successful")
                
                # Trust the device
                subprocess.run(['bluetoothctl', 'trust', mac_address], 
                             capture_output=True, timeout=10)
                return True
            else:
                print(f"Pairing failed: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"Error pairing device: {e}")
            return False
    
    def connect_bluetooth(self, mac_address=None):
        """
        Connect to a Bluetooth speaker.
        
        Args:
            mac_address (str): MAC address of the speaker. If None, uses self.speaker_mac
            
        Returns:
            bool: True if successful
        """
        mac = mac_address or self.speaker_mac
        
        if not mac:
            print("Error: No MAC address provided. Please specify a MAC address.")
            print("Use scan_bluetooth_devices() to find available devices.")
            return False
        
        try:
            print(f"Connecting to Bluetooth speaker {mac}...")
            
            # First, ensure the device is paired
            self.pair_bluetooth_device(mac)
            
            # Connect to the device
            result = subprocess.run(['bluetoothctl', 'connect', mac], 
                                  capture_output=True, text=True, timeout=30)
            
            if "Connection successful" in result.stdout or "already connected" in result.stdout.lower():
                print("Successfully connected to Bluetooth speaker!")
                self.speaker_mac = mac
                
                # Set as default audio sink (PulseAudio)
                time.sleep(2)  # Wait for connection to stabilize
                self._set_default_audio_sink()
                return True
            else:
                print(f"Connection failed: {result.stdout}")
                return False
                
        except Exception as e:
            print(f"Error connecting to Bluetooth device: {e}")
            return False
    
    def disconnect_bluetooth(self, mac_address=None):
        """
        Disconnect from a Bluetooth speaker.
        
        Args:
            mac_address (str): MAC address of the speaker. If None, uses self.speaker_mac
        """
        mac = mac_address or self.speaker_mac
        
        if not mac:
            print("Error: No MAC address provided")
            return False
        
        try:
            print(f"Disconnecting from {mac}...")
            subprocess.run(['bluetoothctl', 'disconnect', mac], 
                         capture_output=True, timeout=10)
            print("Disconnected")
            return True
        except Exception as e:
            print(f"Error disconnecting: {e}")
            return False
    
    def _set_default_audio_sink(self):
        """Set the Bluetooth speaker as the default audio output (PulseAudio)."""
        try:
            # Find the Bluetooth sink
            result = subprocess.run(['pactl', 'list', 'short', 'sinks'], 
                                  capture_output=True, text=True)
            
            for line in result.stdout.split('\n'):
                if 'bluez' in line.lower():
                    sink_name = line.split()[1]
                    subprocess.run(['pactl', 'set-default-sink', sink_name])
                    print(f"Set default audio sink to: {sink_name}")
                    break
                    
        except Exception as e:
            print(f"Note: Could not set default audio sink: {e}")
            print("Audio might still work through the Bluetooth speaker")
        
    def play_local_file(self, file_path):
        """
        Play a local audio file through the Bluetooth speaker.
        
        Args:
            file_path (str): Path to the audio file (mp3, wav, etc.)
        """
        if not os.path.exists(file_path):
            print(f"Error: File {file_path} not found")
            return False
            
        try:
            # Using mpg123 for mp3 files, or ffplay for other formats
            if file_path.endswith('.mp3'):
                self.current_process = subprocess.Popen(['mpg123', file_path])
            else:
                self.current_process = subprocess.Popen(['ffplay', '-nodisp', '-autoexit', file_path])
            print(f"Playing: {file_path}")
            return True
        except FileNotFoundError:
            print("Error: mpg123 or ffplay not installed. Install with: sudo apt-get install mpg123 ffmpeg")
            return False
        except Exception as e:
            print(f"Error playing file: {e}")
            return False
    
    def play_youtube(self, youtube_url):
        """
        Play audio from a YouTube video through the Bluetooth speaker.
        
        Args:
            youtube_url (str): YouTube video URL
        """
        try:
            # Use yt-dlp to stream audio directly without downloading
            # -x extracts audio, --audio-format mp3, -o - pipes to stdout
            print(f"Streaming YouTube audio from: {youtube_url}")
            
            # Method 1: Stream directly using yt-dlp and ffplay
            cmd = f'yt-dlp -x --audio-format mp3 -o - "{youtube_url}" | ffplay -nodisp -autoexit -'
            self.current_process = subprocess.Popen(cmd, shell=True)
            return True
            
        except FileNotFoundError:
            print("Error: yt-dlp not installed. Install with: pip install yt-dlp")
            return False
        except Exception as e:
            print(f"Error playing YouTube video: {e}")
            return False
    
    def play_youtube_download(self, youtube_url, download_dir="/tmp"):
        """
        Download and play audio from a YouTube video.
        
        Args:
            youtube_url (str): YouTube video URL
            download_dir (str): Directory to download the audio file
        """
        try:
            print(f"Downloading YouTube audio from: {youtube_url}")
            
            # Download audio using yt-dlp
            output_template = os.path.join(download_dir, '%(title)s.%(ext)s')
            cmd = ['yt-dlp', '-x', '--audio-format', 'mp3', '-o', output_template, youtube_url]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                # Find the downloaded file
                for file in Path(download_dir).glob("*.mp3"):
                    if file.stat().st_mtime > (os.path.getmtime(download_dir) - 60):  # Modified in last 60 seconds
                        print(f"Downloaded: {file}")
                        return self.play_local_file(str(file))
            else:
                print(f"Download failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"Error downloading/playing YouTube video: {e}")
            return False
    
    def stop(self):
        """Stop the currently playing audio."""
        if self.current_process:
            self.current_process.terminate()
            self.current_process.wait()
            print("Audio stopped")
            self.current_process = None
    
    def is_playing(self):
        """Check if audio is currently playing."""
        if self.current_process:
            return self.current_process.poll() is None
        return False
    
    def wait_until_done(self):
        """Wait until the current audio finishes playing."""
        if self.current_process:
            self.current_process.wait()


# Example usage
if __name__ == "__main__":
    speaker = Speaker()
    
    # Example 1: Scan for Bluetooth devices
    print("=== Scanning for Bluetooth devices ===")
    devices = speaker.scan_bluetooth_devices(scan_time=10)
    
    # Example 2: Connect to a specific speaker (replace with your speaker's MAC)
    # speaker.connect_bluetooth("AA:BB:CC:DD:EE:FF")
    
    # Or initialize with MAC address and connect
    # speaker = Speaker(speaker_mac_address="AA:BB:CC:DD:EE:FF")
    # speaker.connect_bluetooth()
    
    # Example 3: Play a local file
    # speaker.play_local_file("/path/to/your/song.mp3")
    
    # Example 4: Play YouTube video (streaming)
    # speaker.play_youtube("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    # Example 5: Download then play
    # speaker.play_youtube_download("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    
    # Wait for playback to finish
    # speaker.wait_until_done()
    
    # Disconnect when done
    # speaker.disconnect_bluetooth()
    
    print("\nSpeaker module initialized. Use the methods to connect and play audio.")


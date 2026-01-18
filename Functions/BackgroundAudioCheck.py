import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Peripherals.mic import Microphone
from Peripherals.speaker import Speaker
from Peripherals.camera import Camera
import threading
import time
import cv2

class BackgroundAudioCheck:
    def __init__(self, wake_word="hey baymin", speaker_mac=None):
        """
        Initialize the background audio monitoring system.
        
        Args:
            wake_word (str): The wake word to listen for (default: "hey baymin")
            speaker_mac (str): MAC address of Bluetooth speaker for responses
        """
        self.mic = Microphone()
        self.speaker = Speaker(speaker_mac_address=speaker_mac) if speaker_mac else None
        self.camera = Camera()
        
        self.wake_word = wake_word.lower()
        self.is_running = False
        self.listener_thread = None
        
        # Command mapping
        self.commands = {
            "take a picture": self.take_picture,
            "capture image": self.take_picture,
            "take photo": self.take_picture,
            "play music": self.play_music,
            "play song": self.play_music,
            "stop": self.stop_playback,
            "stop music": self.stop_playback,
            "disconnect speaker": self.disconnect_speaker,
            "connect speaker": self.connect_speaker,
            "scan label": self.scan_nutrition_label,
            "read label": self.scan_nutrition_label,
        }
        
    def start_listening(self):
        """Start the background audio monitoring in a separate thread."""
        if self.is_running:
            print("Already listening...")
            return
        
        self.is_running = True
        self.listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
        self.listener_thread.start()
        print(f"Background audio check started. Say '{self.wake_word}' to activate.")
        
    def stop_listening(self):
        """Stop the background audio monitoring."""
        self.is_running = False
        if self.listener_thread:
            self.listener_thread.join(timeout=2)
        print("Background audio check stopped.")
        
    def _listen_loop(self):
        """Main listening loop that runs in the background."""
        while self.is_running:
            try:
                # Listen for the wake word
                print("[DEBUG] Listening for wake word...")
                text = self.mic.listen_for_command(timeout=5, phrase_time_limit=5)
                
                if text:
                    print(f"[DEBUG] Heard: '{text}'")
                    if self.wake_word in text.lower():
                        print(f"[DEBUG] Wake word detected! Listening for command...")
                        self._handle_wake_word()
                    else:
                        print(f"[DEBUG] No wake word in: '{text}'")
                else:
                    print("[DEBUG] No speech detected, continuing to listen...")
                    
            except Exception as e:
                print(f"[DEBUG] Error in listening loop: {e}")
                time.sleep(1)  # Prevent rapid error loops
                
    def _handle_wake_word(self):
        """Handle commands after wake word is detected."""
        try:
            # Open camera window
            camera_thread = threading.Thread(target=self._show_camera_preview, daemon=True)
            camera_thread.start()
            
            # Listen for the actual command
            print("[DEBUG] Waiting for command...")
            command_text = self.mic.listen_for_command(timeout=10, phrase_time_limit=10)
            
            if command_text:
                print(f"[DEBUG] Command received: '{command_text}'")
                self._process_command(command_text.lower())
            else:
                print("[DEBUG] No command detected - timeout")
            
            # Close camera window after command processing
            cv2.destroyAllWindows()
                
        except Exception as e:
            print(f"[DEBUG] Error handling wake word: {e}")
            cv2.destroyAllWindows()
            
    def _show_camera_preview(self):
        """Show camera preview window while listening for commands."""
        try:
            # Initialize camera if needed
            if not self.camera.camera or not self.camera.camera.isOpened():
                self.camera.initialize()
            
            window_name = "Baymin Camera"
            cv2.namedWindow(window_name)
            
            # Show preview for a limited time (10 seconds max)
            start_time = time.time()
            while time.time() - start_time < 10:
                frame = self.camera.capture_image()
                
                if frame is not None:
                    # Add text overlay
                    cv2.putText(frame, "Listening...", (10, 30), 
                               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
                    cv2.imshow(window_name, frame)
                
                # Break if window is closed or 'q' is pressed
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                    
                # Check if window was closed
                if cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE) < 1:
                    break
            
        except Exception as e:
            print(f"Error showing camera preview: {e}")
        finally:
            cv2.destroyAllWindows()
    
    def _process_command(self, command_text):
        """
        Process the recognized command and execute the appropriate function.
        
        Args:
            command_text (str): The recognized command text (lowercased)
        """
        print(f"[DEBUG] Processing command: '{command_text}'")
        
        # Check for exact or partial matches
        for trigger, function in self.commands.items():
            if trigger in command_text:
                print(f"[DEBUG] Matched trigger: '{trigger}' - Executing...")
                try:
                    function(command_text)
                except Exception as e:
                    print(f"[DEBUG] Error executing command '{trigger}': {e}")
                return
        
        # If no command matched
        print(f"[DEBUG] Unknown command: '{command_text}'")
        print(f"[DEBUG] Available commands: {', '.join(self.commands.keys())}")
        
    # Command implementations
    
    def take_picture(self, command_text):
        """Take a picture with the camera."""
        print("Taking picture...")
        image, filepath = self.camera.capture_and_save(save_path="/tmp")
        
        if filepath:
            print(f"Picture saved to: {filepath}")
        else:
            print("Failed to take picture")
            
    def play_music(self, command_text):
        """Play music from YouTube or local file."""
        if not self.speaker:
            print("No speaker configured")
            return
            
        # Extract URL or song name from command
        # Simple example - you can enhance this with NLP
        if "youtube" in command_text or "http" in command_text:
            # Extract URL (simplified)
            words = command_text.split()
            for word in words:
                if "youtube.com" in word or "youtu.be" in word:
                    print(f"Playing YouTube video: {word}")
                    self.speaker.connect_bluetooth()
                    self.speaker.play_youtube(word)
                    return
        
        print("Please specify a YouTube URL in your command")
        
    def stop_playback(self, command_text):
        """Stop audio playback."""
        if self.speaker:
            print("Stopping playback...")
            self.speaker.stop()
        else:
            print("No speaker configured")
            
    def disconnect_speaker(self, command_text):
        """Disconnect Bluetooth speaker."""
        if self.speaker:
            print("Disconnecting speaker...")
            self.speaker.disconnect_bluetooth()
        else:
            print("No speaker configured")
            
    def connect_speaker(self, command_text):
        """Connect Bluetooth speaker."""
        if self.speaker:
            print("Connecting speaker...")
            self.speaker.connect_bluetooth()
        else:
            print("No speaker configured")
            
    def scan_nutrition_label(self, command_text):
        """Scan and read nutrition label using camera and OCR."""
        print("Scanning nutrition label...")
        
        try:
            # Import OCR reader
            from Vision.ocr_reader import OCRReader
            
            # Capture image
            image = self.camera.capture_for_processing()
            
            if image is None:
                print("Failed to capture image")
                return
            
            # Initialize OCR reader
            ocr = OCRReader()
            
            # Extract text
            text = ocr.read_text(image)
            print("Extracted text:")
            print(text)
            
            # You could also send this to an API for analysis
            
        except Exception as e:
            print(f"Error scanning label: {e}")
            
    def add_custom_command(self, trigger, function):
        """
        Add a custom command to the system.
        
        Args:
            trigger (str): The trigger phrase for the command
            function (callable): The function to execute when triggered
        """
        self.commands[trigger.lower()] = function
        print(f"Added custom command: {trigger}")
        
    def cleanup(self):
        """Clean up resources."""
        self.stop_listening()
        self.camera.release()
        self.mic.release()
        if self.speaker:
            self.speaker.disconnect_bluetooth()
        print("Cleanup complete")


# Example usage
if __name__ == "__main__":
    # Initialize with optional speaker MAC address
    # audio_checker = BackgroundAudioCheck(wake_word="hey baymin", speaker_mac="AA:BB:CC:DD:EE:FF")
    audio_checker = BackgroundAudioCheck(wake_word="hey baymin")
    
    try:
        # Start background listening
        audio_checker.start_listening()
        
        # Keep the program running
        print("Press Ctrl+C to stop")
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
        audio_checker.cleanup()

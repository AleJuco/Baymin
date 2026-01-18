"""
Wake word detection using speech recognition
Continuously listens for "hey baymax" and opens camera window
Works on Windows/Mac/Linux
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Peripherals.camera import Camera
from WakeCamera import WakeCameraCapture
import speech_recognition as sr
import time
import cv2

class WakeWordDetector:
    def __init__(self, wake_word="hey", device_index=None):
        """
        Initialize wake word detection with speech recognition.
        
        Args:
            wake_word (str): Wake phrase to listen for
            device_index (int): Microphone device index (None for default)
        """
        self.wake_word = wake_word.lower()
        self.device_index = device_index
        self.camera_capture = WakeCameraCapture()
        self.is_running = False
        self.recognizer = sr.Recognizer()
        
        print(f"Initializing wake word detection...")
        print(f"Wake word: '{wake_word}'")
        
    def initialize(self):
        """Initialize speech recognition."""
        try:
            print("\nListing available microphones:")
            for i, name in enumerate(sr.Microphone.list_microphone_names()):
                print(f"  {i}: {name}")
            
            # Test microphone access
            with sr.Microphone(device_index=self.device_index) as source:
                print(f"\nUsing microphone: {self.device_index or 'default'}")
                print("Adjusting for ambient noise...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print("Ready!")
            
            return True
        except Exception as e:
            print(f"Error initializing: {e}")
            return False
    
    def listen_continuously(self):
        """Continuously listen for the wake word."""
        print("\n" + "=" * 60)
        print("Listening for wake word: '%s'" % self.wake_word)
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        self.is_running = True
        
        try:
            with sr.Microphone(device_index=self.device_index) as source:
                while self.is_running:
                    try:
                        # Listen for speech
                        self.recognizer.adjust_for_ambient_noise(source, duration=0.3)
                        audio = self.recognizer.listen(source, timeout=2, phrase_time_limit=3)
                        
                        # Recognize speech
                        text = self.recognizer.recognize_google(audio).lower()
                        print(f"Heard: '{text}'")
                        
                        # Check for wake word
                        if self.wake_word in text:
                            print("\n" + "=" * 60)
                            print("WAKE WORD DETECTED!")
                            print("=" * 60)
                            
                            # Trigger camera capture and allergy check
                            result = self.camera_capture.capture_on_wake()
                            
                            if result:
                                if isinstance(result, dict):
                                    print(f"\nImage: {result['image_path']}")
                                    print(f"Verdict: {result['verdict']}")
                                    if result['allergies_found']:
                                        print(f"Allergens: {', '.join(result['allergies_found'])}")
                                else:
                                    print(f"Photo saved: {result}")
                            
                            print("\nAnalysis complete. Exiting...")
                            self.is_running = False
                            break
                            
                    except sr.WaitTimeoutError:
                        # No speech detected, continue
                        continue
                    except sr.UnknownValueError:
                        # Speech not understood, continue
                        continue
                    except sr.RequestError as e:
                        print(f"Speech recognition error: {e}")
                        continue
                        
        except KeyboardInterrupt:
            print("\n\nStopping wake word detection...")
        finally:
            self.is_running = False
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        cv2.destroyAllWindows()
        print("Cleanup complete")


if __name__ == "__main__":
    import logging
    
    # Set up logging (ASCII only for Windows compatibility)
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('wake.log', encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info("=" * 60)
    logging.info("BAYMIN WAKE WORD SERVICE STARTING")
    logging.info("=" * 60)
    
    # Create wake word detector
    # Set device_index=None for default mic, or specify a number from the list
    detector = WakeWordDetector(wake_word="hey", device_index=None)
    
    # Initialize
    if detector.initialize():
        logging.info("Initialization successful, starting to listen...")
        # Start listening
        detector.listen_continuously()
    else:
        logging.error("Failed to initialize. Exiting...")
        sys.exit(1)
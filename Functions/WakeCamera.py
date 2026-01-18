"""
Camera capture triggered by wake word
Opens camera window, displays for 5 seconds, and takes a photo
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Peripherals.camera import Camera
from AllergyCheck import AllergyChecker
from VoiceAnnounce import TextToSpeech
import cv2
import time
from datetime import datetime
import os

class WakeCameraCapture:
    def __init__(self, save_path="/tmp/baymin_captures", check_allergies=True):
        """
        Initialize wake camera capture.
        
        Args:
            save_path (str): Directory to save captured images
            check_allergies (bool): Whether to check images for allergens using Gemini
        """
        self.camera = Camera()
        self.save_path = save_path
        self.check_allergies = check_allergies
        
        # Create save directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Initialize allergy checker if enabled
        self.allergy_checker = None
        self.tts = TextToSpeech()  # Initialize TTS
        
        if self.check_allergies:
            try:
                self.allergy_checker = AllergyChecker()
                print("Allergy checker initialized")
            except Exception as e:
                print(f"Allergy checker disabled: {e}")
                self.check_allergies = False
        
    def capture_on_wake(self):
        """
        Take ONE photo immediately when wake word is detected.
        
        Returns:
            str or dict: Path to saved image, or result dict with allergy info
        """
        print("\nWake word detected! Taking photo...")
        
        # Initialize camera
        if not self.camera.initialize():
            print("Failed to initialize camera")
            return None
        
        photo_path = None
        
        try:
            # Warm up camera (Windows needs a few frames)
            for _ in range(10):
                self.camera.capture_image()
                time.sleep(0.1)
            
            # Take the photo
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"wake_{timestamp}.jpg"
            image, photo_path = self.camera.capture_and_save(self.save_path, filename)
            
            if photo_path:
                print(f"Photo saved: {photo_path}")
            else:
                print("Failed to capture photo")
                
        except Exception as e:
            print(f"Error during capture: {e}")
        finally:
            self.camera.release()
            print("Camera closed\n")
        
        # Check for allergies if photo was taken
        if photo_path and self.check_allergies and self.allergy_checker:
            result = self.allergy_checker.check_food_safety(photo_path)
            
            # Announce verdict with TTS including reasoning
            self.tts.announce_verdict(
                safe=result['safe'],
                allergies_found=result['allergies_found'],
                reasoning=result.get('analysis', '')
            )
            
            # Return result with allergy info
            return {
                'image_path': photo_path,
                'safe': result['safe'],
                'allergies_found': result['allergies_found'],
                'verdict': "DO NOT EAT" if result['safe'] is False else "SAFE TO EAT",
                'reasoning': result.get('analysis', '')
            }
        
        return photo_path


if __name__ == "__main__":
    # Test the capture
    capture = WakeCameraCapture()
    path = capture.capture_on_wake()
    if path:
        print(f"Test photo saved to: {path}")

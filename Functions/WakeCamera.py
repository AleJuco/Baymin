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
                print("✓ Allergy checker initialized")
            except Exception as e:
                print(f"⚠️ Allergy checker disabled: {e}")
                self.check_allergies = False
        
    def capture_on_wake(self):
        """
        Open camera window for 5 seconds and take a photo.
        
        Returns:
            str: Path to saved image, or None if failed
        """
        print("\n📷 Wake word detected! Opening camera...")
        
        # Initialize camera
        if not self.camera.initialize():
            print("Failed to initialize camera")
            return None
        
        start_time = time.time()
        countdown = 5
        photo_path = None
        
        try:
            while True:
                # Capture frame
                frame = self.camera.capture_for_processing()
                
                if frame is not None:
                    # Convert to RGB for processing/AI (keep 'frame' as BGR for OpenCV functions)
                    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                    
                    # Calculate remaining time
                    elapsed = time.time() - start_time
                    remaining = max(0, countdown - int(elapsed))
                    
                    # Add countdown overlay
                    text = f"Taking photo in {remaining}s... Press 'q' to cancel"
                    cv2.putText(
                        frame, 
                        text, 
                        (10, 30), 
                        cv2.FONT_HERSHEY_SIMPLEX, 
                        0.7, 
                        (0, 255, 0), 
                        2
                    )
                    
                    # Show frame
                    cv2.imshow('Baymin Wake Camera', frame)
                    
                    # Check if time is up
                    if elapsed >= countdown:
                        # Take the photo
                        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                        filename = f"wake_{timestamp}.jpg"
                        image, photo_path = self.camera.capture_and_save(self.save_path, filename)
                        
                        if photo_path:
                            print(f"✓ Photo saved: {photo_path}")
                        break
                    
                    # Check for cancel key
                    if cv2.waitKey(1) & 0xFF == ord('q'):
                        print("Capture cancelled")
                        break
                
                time.sleep(0.03)  # ~30 FPS
                
        except Exception as e:
            print(f"Error during capture: {e}")
        finally:
            cv2.destroyAllWindows()
            self.camera.release()
            print("📷 Camera closed\n")
        
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

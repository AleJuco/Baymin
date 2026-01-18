"""
Wake word detection using openWakeWord
Continuously listens for a wake phrase and opens camera window
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Peripherals.camera import Camera
from openwakeword.model import Model
from WakeCamera import WakeCameraCapture
import pyaudio
import numpy as np
import threading
import time
import cv2

class OpenWakeWord:
    def __init__(self, wake_word="hey_baymin"):
        """
        Initialize wake word detection with openWakeWord.
        
        Args:
            wake_word (str): Wake word model to use
                Pre-trained: 'alexa', 'hey_jarvis', 'hey_mycroft', 'hey_rhasspy'
        """
        self.wake_word = wake_word
        self.model = None
        self.camera_capture = WakeCameraCapture()
        self.is_running = False
        self.camera_thread = None
        
        # Audio settings
        self.mic_sample_rate = 44100  # HyperX SoloCast native rate
        self.model_sample_rate = 16000  # openWakeWord requires 16kHz
        self.chunk_size = 1280  # 80ms at 16kHz
        self.mic_chunk_size = int(1280 * 44100 / 16000)  # Corresponding 44.1kHz chunk
        self.device_index = 3  # HyperX SoloCast
        
        self.audio = pyaudio.PyAudio()
        
        print(f"Initializing openWakeWord detection...")
        print(f"Wake word: '{wake_word}'")
        
    def initialize(self):
        """Load openWakeWord model and initialize peripherals."""
        try:
            print(f"\nLoading openWakeWord model...")
            
            # Load with default models
            self.model = Model()
            
            print(f"✓ Model loaded")
            print(f"  Available: {list(self.model.models.keys())}")
            
            return True
        except Exception as e:
            print(f"Error initializing openWakeWord: {e}")
            return False
    
    def listen_continuously(self):
        """Continuously listen for the wake word."""
        if not self.model:
            print("Please call initialize() first")
            return
        
        print("\n" + "=" * 60)
        print("🎤 Listening for wake word...")
        print("Press Ctrl+C to stop")
        print("=" * 60 + "\n")
        
        self.is_running = True
        
        # Open audio stream at 44.1kHz
        stream = self.audio.open(
            rate=self.mic_sample_rate,
            channels=1,
            format=pyaudio.paInt16,
            input=True,
            input_device_index=self.device_index,
            frames_per_buffer=self.mic_chunk_size
        )
        
        print("🎧 Ready! Listening...")
        
        try:
            while self.is_running:
                # Read audio chunk at 44.1kHz
                audio_data = np.frombuffer(
                    stream.read(self.mic_chunk_size, exception_on_overflow=False),
                    dtype=np.int16
                )
                
                # Resample to 16kHz for the model
                import scipy.signal
                audio_16k = scipy.signal.resample(audio_data, self.chunk_size)
                
                # Get predictions
                prediction = self.model.predict(audio_16k.astype(np.int16))
                
                # Check if wake word detected (threshold > 0.5)
                for wake_word, score in prediction.items():
                    if score > 0.5:
                        print(f"\n{'='*60}")
                        print(f"✅ WAKE WORD DETECTED: {wake_word} (confidence: {score:.2f})")
                        print("="*60)
                        
                        # Reset model
                        self.model.reset()
                        
                        # Trigger camera capture and allergy check
                        result = self.camera_capture.capture_on_wake()
                        
                        if result:
                            if isinstance(result, dict):
                                # Allergy check was performed
                                print(f"\n{'='*60}")
                                print(f"📸 Image: {result['image_path']}")
                                print(f"🔍 Verdict: {result['verdict']}")
                                if result['allergies_found']:
                                    print(f"⚠️ Allergens: {', '.join(result['allergies_found'])}")
                                print("="*60)
                            else:
                                # Just the path (allergy check disabled)
                                print(f"📸 Photo saved: {result}")
                        
                        # Stop after one detection
                        print("\n✅ Analysis complete. Exiting...")
                        self.is_running = False
                        break
                    
        except KeyboardInterrupt:
            print("\n\n🛑 Stopping wake word detection...")
        finally:
            stream.stop_stream()
            stream.close()
            self.is_running = False
            self.cleanup()
    
    def cleanup(self):
        """Clean up resources."""
        self.is_running = False
        cv2.destroyAllWindows()
        if self.audio:
            self.audio.terminate()
        print("✓ Cleanup complete")


if __name__ == "__main__":
    # Create wake word detector
    detector = OpenWakeWord(wake_word="hey_jarvis")
    
    # Initialize
    if detector.initialize():
        # Start listening
        detector.listen_continuously()

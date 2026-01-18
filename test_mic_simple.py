#!/usr/bin/env python3
"""
Simple microphone test with real-time audio level indicator
"""

import pyaudio
import numpy as np
import sys
import time

# Configuration for HyperX SoloCast
DEVICE_INDEX = 2
SAMPLE_RATE = 44100
CHANNELS = 1
CHUNK_SIZE = 1024

def test_microphone():
    """Test microphone with visual audio level feedback"""
    print("=" * 60)
    print("🎤 HyperX SoloCast Microphone Test")
    print("=" * 60)
    print(f"Device Index: {DEVICE_INDEX}")
    print(f"Sample Rate: {SAMPLE_RATE} Hz")
    print(f"Channels: {CHANNELS}")
    print("\nPress Ctrl+C to stop")
    print("-" * 60)
    
    audio = pyaudio.PyAudio()
    
    try:
        # Open audio stream
        stream = audio.open(
            format=pyaudio.paInt16,
            channels=CHANNELS,
            rate=SAMPLE_RATE,
            input=True,
            input_device_index=DEVICE_INDEX,
            frames_per_buffer=CHUNK_SIZE
        )
        
        print("✓ Microphone stream opened successfully!")
        print("\n🔊 Speak into the microphone to see audio levels:")
        print()
        
        while True:
            # Read audio data
            data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
            
            # Convert to numpy array
            audio_data = np.frombuffer(data, dtype=np.int16)
            
            # Calculate volume (RMS)
            volume = np.sqrt(np.mean(audio_data.astype(np.float64)**2))
            
            # Handle NaN/inf values
            if not np.isfinite(volume):
                volume = 0
            
            # Normalize to 0-50 scale for display
            volume_bar = int(min(volume / 100, 50))
            
            # Create visual bar
            bar = "█" * volume_bar
            
            # Print with carriage return to overwrite
            sys.stdout.write(f"\rLevel: [{bar:<50}] {int(volume):>5}   ")
            sys.stdout.flush()
            
    except KeyboardInterrupt:
        print("\n\n✓ Test stopped by user")
    except Exception as e:
        print(f"\n\n✗ Error: {e}")
    finally:
        # Cleanup
        if 'stream' in locals():
            stream.stop_stream()
            stream.close()
        audio.terminate()
        print("Microphone released")

if __name__ == "__main__":
    test_microphone()

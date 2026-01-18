#!/usr/bin/env python3
"""
Simple microphone test - displays recognized speech in terminal
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from Peripherals.mic import Microphone
from datetime import datetime

def main():
    mic = Microphone()
    
    print("\n" + "=" * 60)
    print("🎤 MICROPHONE TEST")
    print("=" * 60)
    print("\nThis will continuously listen and display what you say.")
    print("Press Ctrl+C to stop.\n")
    print("=" * 60 + "\n")
    
    counter = 1
    
    try:
        while True:
            print(f"\n[{counter}] 🎤 Listening... (speak now)")
            print("-" * 60)
            
            # Listen for speech
            text = mic.listen_for_command(timeout=5, phrase_time_limit=10)
            
            if text:
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"✅ [{timestamp}] HEARD: \"{text}\"")
                print(f"    Length: {len(text)} characters")
                print(f"    Words: {len(text.split())} words")
                counter += 1
            else:
                print("⏳ No speech detected in this cycle")
                
    except KeyboardInterrupt:
        print("\n\n" + "=" * 60)
        print("🛑 Microphone test stopped")
        print(f"Total successful detections: {counter - 1}")
        print("=" * 60 + "\n")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
    finally:
        mic.release()
        print("Microphone released.\n")


if __name__ == "__main__":
    main()

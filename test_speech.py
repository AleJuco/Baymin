#!/usr/bin/env python3
"""
Quick speech recognition test with updated settings
"""

import speech_recognition as sr

print("=" * 60)
print("🎤 Speech Recognition Test (HyperX SoloCast)")
print("=" * 60)
print("Configuration:")
print("  Device Index: 2")
print("  Sample Rate: 44100 Hz")
print("\nSpeak now (10 second timeout)...")
print("-" * 60)

recognizer = sr.Recognizer()

try:
    with sr.Microphone(device_index=2, sample_rate=44100) as source:
        print("🎧 Adjusting for ambient noise... (please be quiet)")
        recognizer.adjust_for_ambient_noise(source, duration=1)
        
        print("✓ Ready! Speak clearly into the microphone...")
        audio = recognizer.listen(source, timeout=10, phrase_time_limit=10)
        
        print("🔄 Processing speech...")
        text = recognizer.recognize_google(audio)
        
        print("\n" + "=" * 60)
        print(f"✓ RECOGNIZED: \"{text}\"")
        print("=" * 60)
        
except sr.WaitTimeoutError:
    print("\n✗ Timeout: No speech detected within 10 seconds")
except sr.UnknownValueError:
    print("\n✗ Could not understand the audio")
except sr.RequestError as e:
    print(f"\n✗ API error: {e}")
except Exception as e:
    print(f"\n✗ Unexpected error: {e}")

#!/usr/bin/env python3
import pyaudio
p = pyaudio.PyAudio()
print("Audio Input Devices:")
print("=" * 60)
for i in range(p.get_device_count()):
    info = p.get_device_info_by_index(i)
    if info['maxInputChannels'] > 0:
        print(f"{i}: {info['name']}")
        print(f"   Channels: {info['maxInputChannels']}, Rate: {info['defaultSampleRate']} Hz")
p.terminate()

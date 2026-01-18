# GLaDOS TTS Setup Instructions

## Installation

1. Clone the GLaDOS TTS repository:
```bash
cd /home/baymini
git clone https://github.com/R2D2KLASKI/glados-tts.git
cd glados-tts
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage Options

### Option 1: Run Locally on Pi
Run the TTS engine directly:
```bash
cd /home/baymini/glados-tts
python3 glados.py "Hello, this is GLaDOS speaking"
```

### Option 2: Run as API Server (Recommended)
Start the TTS server, then call it from your code:

```bash
cd /home/baymini/glados-tts
python3 engine-remote.py
```

Server runs on port 8124. Update your settings.env:
```
TTS_ENGINE_API = http://localhost:8124/synthesize/
```

Then your code can call the API to generate speech.

### Option 3: Run on Another Computer
If your Pi is too slow, run the TTS engine on a more powerful computer:

1. On powerful computer:
```bash
python3 engine-remote.py
```

2. On Pi, set the API URL:
```
TTS_ENGINE_API = http://192.168.1.3:8124/synthesize/
```

Replace `192.168.1.3` with your computer's IP address.

## Integration

I'll update VoiceAnnounce.py to support GLaDOS TTS alongside espeak!

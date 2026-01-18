# Better Text-to-Speech Setup

For more human-like voices, install one of these advanced TTS engines:

## Option 1: MBROLA (Recommended - Most Natural with espeak)

MBROLA voices sound much more human than standard espeak.

```bash
# Install MBROLA
sudo apt-get install mbrola mbrola-us1 mbrola-us2 mbrola-us3

# Test it
espeak -v mb-us1 "Hello, this sounds much better"
```

The system will automatically use MBROLA if installed.

## Option 2: Piper TTS (Best Quality - Neural TTS)

Piper uses neural networks for the most natural-sounding voice:

```bash
# Install piper
pip install piper-tts

# Download a voice model
mkdir -p ~/.local/share/piper/voices
cd ~/.local/share/piper/voices
wget https://github.com/rhasspy/piper/releases/download/v0.0.2/voice-en-us-lessac-medium.tar.gz
tar -xzf voice-en-us-lessac-medium.tar.gz

# Test it
echo "Hello, this sounds very natural" | piper -m en-us-lessac-medium
```

## Option 3: Festival with Better Voices

```bash
# Install festival with nicer voices
sudo apt-get install festival festvox-us-slt-hts

# Test it
echo "Hello there" | festival --tts
```

## Which to Choose?

- **Quick improvement**: Install MBROLA (works immediately with current code)
- **Best quality**: Install Piper (requires code modification)
- **Middle ground**: Festival with HTS voices

## After Installing MBROLA

Just run your existing code - it will automatically detect and use MBROLA voices:

```bash
cd /home/baymini/Baymin/Functions
python VoiceAnnounce.py
```

The voice will be MUCH more natural!

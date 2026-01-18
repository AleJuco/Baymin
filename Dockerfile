FROM python:3.10-slim

# System dependencies for audio, OpenCV, video
RUN apt-get update && apt-get install -y \
    portaudio19-dev \
    libgl1 \
    libglib2.0-0 \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Upgrade pip tooling
RUN pip install --no-cache-dir -U pip setuptools wheel

# Install Python packages (as requested)
RUN pip install --no-cache-dir \
    easyocr==1.7.2 \
    Flask==3.1.2 \
    numpy==2.4.1 \
    opencv-python==4.8.1.78 \
    Pillow>=10.0.0 \
    pyaudio==0.2.14 \
    yt-dlp \
    SpeechRecognition \
    google-generativeai

# Copy your project into the container
COPY . .

# Run your Wave feature
CMD ["python", "Features/Wave.py"]

import pyaudio
import wave
import os
from datetime import datetime
import speech_recognition as sr

class Microphone:
    def __init__(self, sample_rate=16000, channels=1, chunk_size=1024):
        """
        Initialize the Microphone for audio recording and speech recognition.
        
        Args:
            sample_rate (int): Audio sample rate in Hz (16000 is good for speech)
            channels (int): Number of audio channels (1 for mono, 2 for stereo)
            chunk_size (int): Number of frames per buffer
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.chunk_size = chunk_size
        self.format = pyaudio.paInt16  # 16-bit audio
        
        self.audio = None
        self.stream = None
        self.recognizer = sr.Recognizer()
        
    def initialize(self):
        """Initialize PyAudio."""
        try:
            self.audio = pyaudio.PyAudio()
            print("Microphone initialized")
            return True
        except Exception as e:
            print(f"Error initializing microphone: {e}")
            return False
    
    def record_audio(self, duration, save_path=None, filename=None):
        """
        Record audio for a specified duration.
        
        Args:
            duration (int): Recording duration in seconds
            save_path (str): Directory to save the audio file
            filename (str): Filename for the audio (auto-generated if None)
            
        Returns:
            str: Path to saved audio file, or None if failed
        """
        if not self.audio:
            if not self.initialize():
                return None
        
        try:
            print(f"Recording for {duration} seconds...")
            
            # Open stream
            self.stream = self.audio.open(
                format=self.format,
                channels=self.channels,
                rate=self.sample_rate,
                input=True,
                frames_per_buffer=self.chunk_size
            )
            
            frames = []
            
            # Calculate number of chunks to record
            chunks_to_record = int(self.sample_rate / self.chunk_size * duration)
            
            # Record
            for _ in range(chunks_to_record):
                data = self.stream.read(self.chunk_size)
                frames.append(data)
            
            print("Recording complete")
            
            # Stop and close stream
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
            
            # Save to file if path provided
            if save_path or filename:
                return self._save_audio(frames, save_path, filename)
            
            return frames
            
        except Exception as e:
            print(f"Error recording audio: {e}")
            if self.stream:
                self.stream.stop_stream()
                self.stream.close()
                self.stream = None
            return None
    
    def _save_audio(self, frames, save_path=None, filename=None):
        """Save recorded audio frames to a WAV file."""
        # Generate filename if not provided
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recording_{timestamp}.wav"
        
        # Set default save path
        if save_path is None:
            save_path = "/tmp"
        
        # Create directory if it doesn't exist
        os.makedirs(save_path, exist_ok=True)
        
        # Full filepath
        filepath = os.path.join(save_path, filename)
        
        try:
            # Save as WAV file
            with wave.open(filepath, 'wb') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(self.audio.get_sample_size(self.format))
                wf.setframerate(self.sample_rate)
                wf.writeframes(b''.join(frames))
            
            print(f"Audio saved to: {filepath}")
            return filepath
            
        except Exception as e:
            print(f"Error saving audio: {e}")
            return None
    
    def listen_for_command(self, timeout=5, phrase_time_limit=10):
        """
        Listen for a voice command and convert it to text.
        
        Args:
            timeout (int): Maximum time to wait for speech to start (seconds)
            phrase_time_limit (int): Maximum time for the phrase (seconds)
            
        Returns:
            str: Recognized text, or None if failed
        """
        try:
            with sr.Microphone(sample_rate=self.sample_rate) as source:
                print("Listening for command...")
                
                # Adjust for ambient noise
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                
                # Listen for audio
                audio = self.recognizer.listen(
                    source, 
                    timeout=timeout,
                    phrase_time_limit=phrase_time_limit
                )
                
                print("Processing speech...")
                
                # Recognize speech using Google Speech Recognition
                text = self.recognizer.recognize_google(audio)
                print(f"Recognized: {text}")
                return text
                
        except sr.WaitTimeoutError:
            print("Listening timed out - no speech detected")
            return None
        except sr.UnknownValueError:
            print("Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"Error with speech recognition service: {e}")
            return None
        except Exception as e:
            print(f"Error listening for command: {e}")
            return None
    
    def listen_continuously(self, callback, timeout=None):
        """
        Continuously listen for commands and call callback function with recognized text.
        
        Args:
            callback (function): Function to call with recognized text
            timeout (int): Stop after this many seconds (None for infinite)
        """
        print("Starting continuous listening... (Press Ctrl+C to stop)")
        
        try:
            start_time = datetime.now()
            
            while True:
                # Check timeout
                if timeout and (datetime.now() - start_time).seconds > timeout:
                    break
                
                # Listen for command
                text = self.listen_for_command(timeout=5)
                
                if text:
                    callback(text)
                    
        except KeyboardInterrupt:
            print("\nStopped listening")
    
    def release(self):
        """Release audio resources."""
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
            self.stream = None
        
        if self.audio:
            self.audio.terminate()
            self.audio = None
            print("Microphone released")
    
    def __del__(self):
        """Ensure resources are released when object is destroyed."""
        self.release()


# Example usage
if __name__ == "__main__":
    mic = Microphone()
    
    # Example 1: Record audio for 5 seconds
    # audio_file = mic.record_audio(duration=5, save_path="/tmp", filename="test.wav")
    
    # Example 2: Listen for a voice command
    command = mic.listen_for_command(timeout=10)
    if command:
        print(f"You said: {command}")
    
    # Example 3: Continuous listening
    # def handle_command(text):
    #     print(f"Command received: {text}")
    # 
    # mic.listen_continuously(callback=handle_command, timeout=60)
    
    # Release resources
    mic.release() 
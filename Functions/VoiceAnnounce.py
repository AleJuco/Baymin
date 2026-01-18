"""
Text-to-Speech module for announcing verdicts
Uses multiple TTS engines with fallback options
"""

import subprocess
import os
import sys
import requests
import tempfile

class TextToSpeech:
    def __init__(self, engine='auto', glados_api='http://localhost:8124/synthesize'):
        """
        Initialize TTS engine.
        
        Args:
            engine (str): TTS engine to use ('auto', 'glados', 'espeak', 'pyttsx3', 'festival')
            glados_api (str): GLaDOS TTS API endpoint
        """
        self.engine = engine
        self.glados_api = glados_api
        self.available_engine = self._detect_engine()
        
    def _detect_engine(self):
        """Detect which TTS engine is available."""
        # If auto mode, check for GLaDOS first
        if self.engine == 'auto' or self.engine == 'glados':
            if self._check_glados():
                print("✓ Using GLaDOS neural TTS engine")
                return 'glados'
        
        # Check for gTTS (Google TTS)
        if self.engine == 'auto' or self.engine == 'gtts':
            try:
                from gtts import gTTS
                print("✓ Using Google Text-to-Speech (gTTS)")
                return 'gtts'
            except ImportError:
                pass
        
        # Check for espeak
        try:
            result = subprocess.run(['which', 'espeak'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                print("✓ Using espeak TTS engine")
                return 'espeak'
        except:
            pass
        
        # Check for festival
        try:
            result = subprocess.run(['which', 'festival'], 
                                   capture_output=True, 
                                   text=True)
            if result.returncode == 0:
                print("✓ Using festival TTS engine")
                return 'festival'
        except:
            pass
        
        # Try pyttsx3 (Python library)
        try:
            import pyttsx3
            print("✓ Using pyttsx3 TTS engine")
            return 'pyttsx3'
        except ImportError:
            pass
        
        print("⚠️ No TTS engine found. Install with:")
        print("   sudo apt-get install espeak")
        print("   Or set up GLaDOS TTS (see GLADOS_TTS_SETUP.md)")
        return None
    
    def _check_glados(self):
        """Check if GLaDOS TTS API is available."""
        try:
            print("🔍 Checking for GLaDOS server at", self.glados_api)
            response = requests.get(self.glados_api.replace('/synthesize', '/'), timeout=2)
            print(f"   Response: {response.status_code}")
            return response.status_code == 200 or response.status_code == 404  # 404 is ok, means server is up
        except requests.exceptions.ConnectionError as e:
            print(f"   ❌ GLaDOS server not running: Connection refused")
            return False
        except requests.exceptions.Timeout:
            print(f"   ❌ GLaDOS server timeout")
            return False
        except Exception as e:
            print(f"   ❌ GLaDOS check failed: {e}")
            return False
    
    def speak(self, text, rate=150, volume=100):
        """
        Speak the given text.
        
        Args:
            text (str): Text to speak
            rate (int): Speech rate (words per minute)
            volume (int): Volume level (0-100)
        """
        if not self.available_engine:
            print(f"TTS: {text}")
            return
        
        print(f"🔊 Speaking: {text}")
        
        try:
            if self.available_engine == 'glados':
                self._speak_glados(text)
            elif self.available_engine == 'gtts':
                self._speak_gtts(text)
            elif self.available_engine == 'espeak':
                self._speak_espeak(text, rate, volume)
            elif self.available_engine == 'festival':
                self._speak_festival(text)
            elif self.available_engine == 'pyttsx3':
                self._speak_pyttsx3(text, rate, volume)
        except Exception as e:
            print(f"Error speaking: {e}")
    
    def _speak_glados(self, text):
        """Speak using GLaDOS neural TTS API."""
        try:
            # Call GLaDOS API
            response = requests.post(
                self.glados_api,
                json={'text': text},
                timeout=10
            )
            
            if response.status_code == 200:
                # Save audio to temp file
                with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as f:
                    f.write(response.content)
                    audio_file = f.name
                
                # Play audio with aplay (ALSA player)
                subprocess.run(['aplay', '-q', audio_file])
                
                # Clean up
                os.unlink(audio_file)
            else:
                print(f"GLaDOS API error: {response.status_code}")
                # Fallback to espeak
                self._speak_espeak(text, 150, 100)
                
        except Exception as e:
            print(f"GLaDOS TTS error: {e}")
            # Fallback to espeak
            try:
                self._speak_espeak(text, 150, 100)
            except:
                print(f"TTS: {text}")
    
    def _speak_gtts(self, text):
        """Speak using Google Text-to-Speech (gTTS) - natural voice, needs internet."""
        try:
            from gtts import gTTS
            
            # Generate audio
            tts = gTTS(text=text, lang='en', slow=False)
            
            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as f:
                audio_file = f.name
            
            tts.save(audio_file)
            
            # Play audio with mpg123 or ffplay
            try:
                subprocess.run(['mpg123', '-q', audio_file])
            except FileNotFoundError:
                # Try ffplay if mpg123 not available
                try:
                    subprocess.run(['ffplay', '-nodisp', '-autoexit', audio_file], 
                                 stderr=subprocess.DEVNULL)
                except FileNotFoundError:
                    # Try aplay with conversion (requires ffmpeg)
                    subprocess.run(['ffmpeg', '-i', audio_file, '-f', 'wav', '-', '|', 'aplay'], 
                                 shell=True, stderr=subprocess.DEVNULL)
            
            # Clean up
            os.unlink(audio_file)
            
        except Exception as e:
            print(f"gTTS error: {e}")
            # Fallback to espeak
            self._speak_espeak(text, 175, 100)
    
    def _speak_espeak(self, text, rate=150, volume=100):
        """Speak using espeak with the warmest, friendliest voice possible."""
        # Try different voice variants for most natural sound
        subprocess.run([
            'espeak',
            '-s', '175',  # Conversational speed
            '-a', str(volume),
            '-v', 'en+f2',  # Softer female variant
            '-p', '60',  # Warmer, higher pitch
            text
        ])
    
    def _speak_festival(self, text):
        """Speak using festival."""
        process = subprocess.Popen(
            ['festival', '--tts'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        process.communicate(input=text.encode())
    
    def _speak_pyttsx3(self, text, rate=150, volume=1.0):
        """Speak using pyttsx3."""
        import pyttsx3
        engine = pyttsx3.init()
        engine.setProperty('rate', rate)
        engine.setProperty('volume', volume / 100.0)
        engine.say(text)
        engine.runAndWait()
    
    def _simplify_reasoning(self, reasoning):
        """
        Convert technical reasoning into natural speech.
        
        Args:
            reasoning (str): Technical reasoning from Gemini API
            
        Returns:
            str: Simplified, conversational explanation
        """
        if not reasoning:
            return ""
        
        # Remove overly technical language and make it conversational
        simplified = reasoning
        
        # Shorten common phrases
        replacements = {
            "The visible food item in the image is": "This looks like",
            "displayed on a smartphone screen": "on your screen",
            "in their natural state": "",
            "do not contain": "don't have",
            "No ingredient labels, processing information, or cross-contamination warnings are visible": "I don't see any warning labels",
            "that would indicate the presence of": "showing",
            "or their derivatives": "",
            "Therefore, based on the visual evidence": "So",
            "regarding the specified allergens": "for your allergies",
            "itself is safe": "is safe",
        }
        
        for old, new in replacements.items():
            simplified = simplified.replace(old, new)
        
        # Limit to first 2 sentences for brevity
        sentences = simplified.split('. ')
        if len(sentences) > 2:
            simplified = '. '.join(sentences[:2]) + '.'
        
        return simplified.strip()
    
    def announce_verdict(self, safe, allergies_found=None, reasoning=None):
        """
        Announce allergy check verdict with optional reasoning.
        
        Args:
            safe (bool): Whether food is safe to eat
            allergies_found (list): List of allergens detected
            reasoning (str): Detailed reasoning from allergen analysis
        """
        import random
        
        # Simplify reasoning if provided
        simplified_reasoning = self._simplify_reasoning(reasoning) if reasoning else ""
        
        if safe is False:
            # Unsafe - caring warning
            if allergies_found:
                allergens = ', '.join(allergies_found)
                messages = [
                    f"Please be careful! This contains {allergens}, which you're allergic to.",
                    f"I detected {allergens} in this food. It's not safe for you to eat.",
                    f"Warning: this has {allergens}. Please don't eat this.",
                ]
                message = random.choice(messages)
                
                # Add simplified reasoning if available
                if simplified_reasoning:
                    message += " " + simplified_reasoning
                
                self.speak(message, rate=150, volume=100)
            else:
                messages = [
                    "Please don't eat this. It's not safe for you.",
                    "I recommend you avoid this food.",
                    "This isn't safe for you to eat.",
                ]
                message = random.choice(messages)
                
                # Add simplified reasoning if available
                if simplified_reasoning:
                    message += " " + simplified_reasoning
                
                self.speak(message, rate=150, volume=100)
        elif safe is True:
            # Safe - warm approval
            messages = [
                "Great news! This is safe for you to eat.",
                "You're all clear! No allergens detected.",
                "This looks safe! Enjoy your meal.",
                "All good! No allergens found.",
            ]
            message = random.choice(messages)
            
            # Add simplified reasoning if available
            if simplified_reasoning:
                message += " " + simplified_reasoning
            
            self.speak(message, rate=160, volume=85)
        else:
            # Unable to determine - gentle uncertainty
            messages = [
                "I'm not sure about this one. Please check the label to be safe.",
                "I couldn't identify all the ingredients. Better to be cautious.",
                "I'm unable to verify this is safe. Please double check before eating.",
            ]
            message = random.choice(messages)
            
            # Add simplified reasoning if available
            if simplified_reasoning:
                message += " " + simplified_reasoning
            
            self.speak(message, rate=155, volume=80)


def main():
    """Test TTS functionality."""
    import sys
    
    tts = TextToSpeech()
    
    if len(sys.argv) > 1:
        # Speak provided text
        text = ' '.join(sys.argv[1:])
        tts.speak(text)
    else:
        # Test verdicts
        print("\nTesting SAFE verdict:")
        tts.announce_verdict(safe=True)
        
        print("\nWaiting 2 seconds...")
        import time
        time.sleep(2)
        
        print("\nTesting UNSAFE verdict:")
        tts.announce_verdict(safe=False, allergies_found=['Peanuts', 'Tree Nuts'])


if __name__ == "__main__":
    main()

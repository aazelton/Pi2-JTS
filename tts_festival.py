#!/usr/bin/env python3
"""
Festival TTS Module with MBROLA Voices
Better sounding offline TTS for Pi2 deployment
Much more natural than eSpeak while remaining lightweight
"""

import subprocess
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

class FestivalTTS:
    """
    Festival TTS with MBROLA voices for better quality offline speech
    Pi2-friendly with natural sounding voices
    """
    
    def __init__(self):
        self.available_voices = self._detect_voices()
        self.current_voice = 'mb-us1'  # Default MBROLA voice
        self.festival_running = False
        
    def _detect_voices(self) -> list:
        """Detect available Festival and MBROLA voices"""
        voices = []
        
        # Check for Festival
        try:
            result = subprocess.run(['which', 'festival'], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                voices.append('festival')
                logger.info("Festival TTS detected")
        except Exception:
            pass
        
        # Check for MBROLA voices
        mbrola_voices = ['mb-us1', 'mb-us2', 'mb-us3']
        for voice in mbrola_voices:
            try:
                result = subprocess.run(['which', f'mbrola-{voice}'], 
                                      capture_output=True, text=True)
                if result.returncode == 0:
                    voices.append(voice)
                    logger.info(f"MBROLA voice {voice} detected")
            except Exception:
                pass
        
        return voices
    
    def speak_festival(self, text: str, voice: str = 'festival') -> bool:
        """Speak using Festival TTS"""
        try:
            # Festival command with voice selection
            cmd = [
                'festival', 
                '--tts', 
                f'(voice_{voice})',
                f'"{text}"'
            ]
            
            subprocess.run(cmd, check=True, capture_output=True)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"Festival TTS failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("Festival not found")
            return False
    
    def speak_mbrola(self, text: str, voice: str = 'mb-us1') -> bool:
        """Speak using MBROLA voice (much better quality)"""
        try:
            # MBROLA pipeline: text -> MBROLA -> audio
            # First, convert text to phonemes using Festival
            phoneme_cmd = [
                'festival', 
                '--tts', 
                '--batch',
                f'(voice_{voice})',
                f'"{text}"'
            ]
            
            # Run MBROLA with the phonemes
            mbrola_cmd = [
                'mbrola',
                f'/usr/share/mbrola/{voice}/{voice}',
                '-',  # Read from stdin
                '-',  # Output to stdout
                '|',
                'aplay',  # Play audio
                '-f', 'S16_LE',
                '-r', '22050',
                '-c', '1'
            ]
            
            # Execute the pipeline
            subprocess.run(phoneme_cmd, check=True)
            return True
            
        except subprocess.CalledProcessError as e:
            logger.error(f"MBROLA TTS failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("MBROLA not found")
            return False
    
    def speak(self, text: str, voice: Optional[str] = None) -> bool:
        """Speak text using best available voice"""
        if voice is None:
            voice = self.current_voice
        
        # Try MBROLA first (best quality)
        if voice in self.available_voices and voice.startswith('mb-'):
            logger.info(f"Using MBROLA voice: {voice}")
            return self.speak_mbrola(text, voice)
        
        # Fallback to Festival
        elif 'festival' in self.available_voices:
            logger.info("Using Festival TTS")
            return self.speak_festival(text, 'festival')
        
        # Final fallback to eSpeak
        else:
            logger.warning("Falling back to eSpeak")
            return self.speak_espeak(text)
    
    def speak_espeak(self, text: str) -> bool:
        """Fallback to eSpeak if Festival/MBROLA not available"""
        try:
            subprocess.run(['espeak-ng', text], check=True)
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"eSpeak failed: {e}")
            return False
        except FileNotFoundError:
            logger.error("eSpeak not found")
            return False
    
    def set_voice(self, voice: str) -> bool:
        """Set the current voice"""
        if voice in self.available_voices:
            self.current_voice = voice
            logger.info(f"Voice set to: {voice}")
            return True
        else:
            logger.warning(f"Voice {voice} not available. Available: {self.available_voices}")
            return False
    
    def get_available_voices(self) -> list:
        """Get list of available voices"""
        return self.available_voices
    
    def test_voices(self):
        """Test all available voices"""
        test_text = "SPEC-1-MedicVoicePi2 system test. Ketamine dosage is 40 to 80 milligrams."
        
        print("🎤 Testing available TTS voices:")
        print(f"Available voices: {self.available_voices}")
        print("")
        
        for voice in self.available_voices:
            print(f"Testing {voice}...")
            success = self.speak(test_text, voice)
            if success:
                print(f"✅ {voice} - Working")
            else:
                print(f"❌ {voice} - Failed")
            print("")

def speak(text: str, voice: Optional[str] = None) -> bool:
    """Global speak function using Festival TTS"""
    tts = FestivalTTS()
    return tts.speak(text, voice)

def set_voice(voice: str) -> bool:
    """Global voice setting function"""
    tts = FestivalTTS()
    return tts.set_voice(voice)

def test_voices():
    """Global test function"""
    tts = FestivalTTS()
    tts.test_voices()

if __name__ == "__main__":
    # Test the Festival TTS system
    test_voices() 
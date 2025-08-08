#!/usr/bin/env python3
"""
Text-to-Speech utilities for P2 JTS Clinical Assist
Provides multiple voice options with better quality settings
Uses Festival with MBROLA voices for best quality
"""

import subprocess
import platform
import os
import logging

logger = logging.getLogger(__name__)

class TTSManager:
    def __init__(self, voice_preference="mb-us1"):
        self.voice_preference = voice_preference
        self.system = platform.system()
        
    def speak_festival_mbrola(self, text):
        """Use Festival with MBROLA voices (best quality)"""
        try:
            # Try Festival with MBROLA first (best quality)
            cmd = [
                'festival', 
                '--tts', 
                f'(voice_{self.voice_preference})',
                f'"{text}"'
            ]
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            logger.info(f"Festival MBROLA voice {self.voice_preference} used successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"Festival MBROLA failed: {e}")
            return False
    
    def speak_festival(self, text):
        """Use Festival TTS (good quality)"""
        try:
            cmd = ['festival', '--tts', f'"{text}"']
            subprocess.run(cmd, check=True, capture_output=True, timeout=10)
            logger.info("Festival TTS used successfully")
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
            logger.debug(f"Festival failed: {e}")
            return False
    
    def speak_enhanced_say(self, text):
        """Use macOS 'say' with enhanced settings for better quality"""
        if self.system == "Darwin":
            try:
                # Force Samantha voice for consistent quality
                voice = "Samantha"
                rate = "130"
                
                # Enhanced settings for more natural speech
                cmd = [
                    "say", 
                    "-v", voice, 
                    "-r", rate,      # Slightly slower for clarity
                    text
                ]
                result = subprocess.run(cmd, check=True, timeout=15, capture_output=True)
                logger.info(f"Enhanced say voice {voice} used successfully")
                return True
            except Exception as e:
                logger.debug(f"Enhanced say failed: {e}")
                return False
        return False
    
    def speak_espeak_enhanced(self, text):
        """Enhanced espeak with better settings for clinical use"""
        try:
            # Enhanced settings for better voice quality
            cmd = [
                "espeak-ng",
                "-v", self.voice_preference,  # Voice selection
                "-s", "140",                  # Speed (slower for clarity)
                "-p", "60",                   # Pitch (slightly higher)
                "-a", "120",                  # Amplitude (louder)
                "-g", "5",                    # Word gap (small pause between words)
                "-k", "5",                    # Emphasis (slight emphasis on keywords)
                text
            ]
            subprocess.run(cmd, check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def speak_espeak_simple(self, text):
        """Fallback to simple espeak"""
        try:
            subprocess.run(["espeak-ng", text], check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def speak(self, text):
        """Main speak function that tries multiple TTS options in quality order"""
        # 1. Try Festival with MBROLA first (best quality)
        if self.speak_festival_mbrola(text):
            return True
        
        # 2. Try Festival TTS (good quality)
        if self.speak_festival(text):
            return True
        
        # 3. Try enhanced macOS say (better than default)
        if self.speak_enhanced_say(text):
            return True
        
        # 4. Try enhanced espeak as fallback
        if self.speak_espeak_enhanced(text):
            return True
        
        # 5. Fallback to simple espeak
        if self.speak_espeak_simple(text):
            return True
        
        # 6. Last resort - print to console
        print(f"SPEAK: {text}")
        return False

# Global TTS manager instance with MBROLA preference
tts_manager = TTSManager("mb-us1")

def speak(text):
    """Global speak function for easy use"""
    return tts_manager.speak(text)

def set_voice(voice_name):
    """Change the voice preference"""
    global tts_manager
    tts_manager.voice_preference = voice_name 
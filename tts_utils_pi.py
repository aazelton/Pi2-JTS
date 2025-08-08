#!/usr/bin/env python3
"""
Text-to-Speech utilities optimized for Raspberry Pi
Lightweight and efficient voice options for Pi2 with 128GB SD card
"""

import subprocess
import platform
import os

class TTSManagerPi:
    def __init__(self, voice_preference="en-us"):
        self.voice_preference = voice_preference
        self.system = platform.system()
        
    def speak_espeak_optimized(self, text):
        """Optimized espeak settings for Raspberry Pi - good balance of quality and performance"""
        try:
            # Optimized settings for Pi performance
            cmd = [
                "espeak",
                "-v", self.voice_preference,  # Voice selection
                "-s", "130",                  # Speed (good for clinical clarity)
                "-p", "55",                   # Pitch (natural range)
                "-a", "110",                  # Amplitude (clear but not too loud)
                "-g", "3",                    # Word gap (small pause)
                text
            ]
            subprocess.run(cmd, check=True, timeout=15)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def speak_espeak_fast(self, text):
        """Fast espeak for quick responses"""
        try:
            cmd = [
                "espeak",
                "-v", self.voice_preference,
                "-s", "150",                  # Faster speed
                "-p", "50",
                "-a", "100",
                text
            ]
            subprocess.run(cmd, check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def speak_espeak_simple(self, text):
        """Fallback to simple espeak"""
        try:
            subprocess.run(["espeak", text], check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def speak_say_linux(self, text):
        """Use Linux 'say' command if available (some Pi distributions have it)"""
        try:
            # Try to use a natural voice if available
            cmd = ["say", "-r", "130", text]
            subprocess.run(cmd, check=True, timeout=10)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    def speak(self, text):
        """Main speak function optimized for Pi performance"""
        # Try optimized espeak first (best balance)
        if self.speak_espeak_optimized(text):
            return True
        
        # Try fast espeak for quick responses
        if self.speak_espeak_fast(text):
            return True
        
        # Try Linux say command
        if self.speak_say_linux(text):
            return True
        
        # Fallback to simple espeak
        if self.speak_espeak_simple(text):
            return True
        
        # Last resort - print to console
        print(f"SPEAK: {text}")
        return False

# Global TTS manager instance for Pi
tts_manager_pi = TTSManagerPi()

def speak(text):
    """Global speak function for Pi"""
    return tts_manager_pi.speak(text)

def set_voice(voice_name):
    """Change the voice preference"""
    global tts_manager_pi
    tts_manager_pi.voice_preference = voice_name

def test_voices():
    """Test different voice configurations"""
    test_text = "Testing voice quality for clinical use"
    
    print("Testing optimized espeak...")
    speak(test_text)
    
    print("Testing different voice settings...")
    set_voice("en-uk")
    speak(test_text)
    
    set_voice("en-us")
    speak(test_text) 
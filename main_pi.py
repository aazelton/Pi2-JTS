#!/usr/bin/env python3
"""
P2 JTS Clinical Assist - Raspberry Pi Optimized Version
Uses optimized TTS settings for better performance on Pi2 with 128GB SD card
"""

from airway_tree import build_tree
from vosk import Model, KaldiRecognizer
import pyaudio
import subprocess
import json
from tts_utils_pi import speak, set_voice

def listen(model):
    rec = KaldiRecognizer(model, 16000)
    mic = pyaudio.PyAudio().open(format=pyaudio.paInt16, channels=1,
                                 rate=16000, input=True, frames_per_buffer=8192)
    mic.start_stream()
    while True:
        data = mic.read(4096, exception_on_overflow=False)
        if rec.AcceptWaveform(data):
            result = json.loads(rec.Result())
            return result.get("text", "")

def main():
    print("Initializing P2 JTS Clinical Assist (Pi Optimized)...")
    
    # Load speech recognition model
    print("Loading speech recognition model...")
    model = Model("models/vosk-model-small-en-us-0.15")
    
    # Set voice preference for clinical use
    set_voice("en-us")  # US English for clinical clarity
    
    # Build decision tree
    current = build_tree()
    
    print("System ready. Starting clinical protocol...")
    
    while current:
        # Speak the prompt with optimized settings
        speak(current.prompt)
        
        # Listen for response
        user_input = listen(model)
        print("User said:", user_input)
        
        if current.is_terminal:
            speak("Protocol complete.")
            break
            
        current = current.get_next(user_input)
        if current is None:
            speak("Sorry, I didn't understand. Please say yes or no.")
            current = build_tree()

if __name__ == "__main__":
    main() 
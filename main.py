from airway_tree import build_tree
from vosk import Model, KaldiRecognizer
import pyaudio
import subprocess
import json
from tts_utils import speak, set_voice
import logging

# Set up logging to see which TTS system is being used
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_best_microphone():
    """Get the best available microphone"""
    p = pyaudio.PyAudio()
    best_device = None
    
    # Look for built-in microphone first (usually more reliable)
    for i in range(p.get_device_count()):
        info = p.get_device_info_by_index(i)
        if info['maxInputChannels'] > 0:  # Has input capability
            name = info['name'].lower()
            # Prefer built-in microphone
            if 'imac' in name or 'built-in' in name or 'internal' in name:
                best_device = i
                break
            # Fallback to any input device
            elif best_device is None:
                best_device = i
    
    p.terminate()
    return best_device

def listen(model):
    rec = KaldiRecognizer(model, 16000)
    
    # Get best microphone
    mic_device = get_best_microphone()
    if mic_device is None:
        print("❌ No microphone found!")
        return ""
    
    print(f"🎤 Using microphone device: {mic_device}")
    
    p = pyaudio.PyAudio()
    mic = p.open(
        format=pyaudio.paInt16, 
        channels=1,
        rate=16000, 
        input=True, 
        input_device_index=mic_device,
        frames_per_buffer=8192
    )
    
    print("🎤 Listening... (speak clearly)")
    
    try:
        while True:
            data = mic.read(4096, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:  # Only return if we got actual text
                    return text
    except KeyboardInterrupt:
        print("\n🛑 Listening stopped")
        return ""
    finally:
        mic.stop_stream()
        mic.close()
        p.terminate()

def test_voice_quality():
    """Test voice quality with different TTS systems"""
    print("🎤 Testing voice quality...")
    test_text = "SPEC-1-MedicVoicePi2 system test. Ketamine dosage is 40 to 80 milligrams IV or IM."
    speak(test_text)
    print("✅ Voice test completed")

def main():
    print("🎤 SPEC-1-MedicVoicePi2 - Enhanced Voice System")
    print("===============================================")
    print("Using Samantha voice for smooth, natural communication")
    print("")
    
    # Test voice quality first
    test_voice_quality()
    print("")
    
    model = Model("models/vosk-model-small-en-us-0.15")
    current = build_tree()
    
    print("🎤 Starting voice interaction...")
    print("Speak clearly into your microphone")
    print("")
    
    while current:
        speak(current.prompt)
        user_input = listen(model)
        print(f"User said: '{user_input}'")
        
        if not user_input:
            print("❌ No speech detected. Please try again.")
            continue
            
        if current.is_terminal:
            speak("Protocol complete.")
            break
        current = current.get_next(user_input)
        if current is None:
            speak("Sorry, I didn't understand. Please say yes or no.")
            current = build_tree()

if __name__ == "__main__":
    main()

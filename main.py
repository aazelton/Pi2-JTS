from airway_tree import build_tree
from vosk import Model, KaldiRecognizer
import pyaudio
import subprocess
import json

def speak(text):
    subprocess.run(["espeak", text])

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
    model = Model("models/vosk-model-small-en-us-0.15")
    current = build_tree()
    while current:
        speak(current.prompt)
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

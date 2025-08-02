# Offline Clinical Support System (Raspberry Pi 2)

A fully offline, speech-only clinical decision support system designed for Raspberry Pi 2. Based on Joint Trauma System (JTS) protocols and optimized for low-power, low-resource environments.

## Features

- Voice-driven clinical decision making
- Built-in offline speech-to-text (Vosk)
- Lightweight text-to-speech (eSpeak NG)
- Local-only operation (no cloud dependencies)
- Headless: just plug in headphones and mic

## Hardware Requirements

- Raspberry Pi 2 (ARMv7, 1GB RAM)
- USB Microphone and 3.5mm headphones
- MicroSD card (>= 8GB)
- No display needed

## Installation

### 1. Install dependencies

```bash
sudo apt update
sudo apt install python3-pyaudio portaudio19-dev espeak-ng unzip wget -y
pip3 install -r requirements.txt
```

### 2. Download Vosk STT model

```bash
mkdir -p models
cd models
wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
```

### 3. Run the app

```bash
python3 main.py
```

## Auto-run on boot (optional)

Use `systemd` to run `main.py` on boot (see documentation for instructions).

## Licensing

This project is licensed under Creative Commons Attribution 4.0 International (CC BY 4.0). See [LICENSE](LICENSE) for details.

## Author

Made by [sammuti.com](https://sammuti.com)

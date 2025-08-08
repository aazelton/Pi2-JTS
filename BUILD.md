# P2 JTS Clinical Assist - Build Instructions

## Prerequisites

- Python 3.13 or later
- macOS (tested on macOS 14.5.0)
- Homebrew (for installing system dependencies)

## System Dependencies

Install required system packages:

```bash
# Install portaudio (required for PyAudio)
brew install portaudio

# Install espeak (text-to-speech)
brew install espeak
```

## Python Environment Setup

1. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   ```

2. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

3. **Upgrade pip:**
   ```bash
   pip install --upgrade pip
   ```

4. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

## Speech Recognition Model

The application requires a Vosk speech recognition model:

1. **Create models directory:**
   ```bash
   mkdir -p models
   ```

2. **Download the model:**
   ```bash
   cd models
   curl -L -o vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
   ```

3. **Extract the model:**
   ```bash
   unzip vosk-model-small-en-us-0.15.zip
   rm vosk-model-small-en-us-0.15.zip
   cd ..
   ```

## Testing the Build

Run the test script to verify everything is working:

```bash
source venv/bin/activate
python test_imports.py
```

You should see all tests pass with checkmarks.

## Running the Application

### Option 1: Using the startup script
```bash
./run.sh
```

### Option 2: Manual execution
```bash
source venv/bin/activate
python main.py
```

## Troubleshooting

### PyAudio Installation Issues
If PyAudio fails to install, try:
```bash
pip install --no-binary :all: pyaudio
```

### Microphone Access
Make sure your application has microphone access:
- Go to System Preferences > Security & Privacy > Privacy > Microphone
- Add your terminal application or Python to the allowed list

### Model Download Issues
If the model download fails, you can manually download it from:
https://alphacephei.com/vosk/models/

## Project Structure

```
Pi2-JTS/
├── main.py              # Main application entry point
├── airway_tree.py       # Decision tree logic
├── requirements.txt     # Python dependencies
├── run.sh              # Startup script
├── test_imports.py     # Import test script
├── venv/               # Virtual environment
└── models/             # Speech recognition models
    └── vosk-model-small-en-us-0.15/
```

## Features

- **Speech Recognition**: Uses Vosk for accurate speech-to-text conversion
- **Text-to-Speech**: Uses natural-sounding voices (Kathy, Samantha, Fred) via macOS 'say' command
- **Clinical Decision Tree**: Guides through airway management protocols
- **Voice Interaction**: Hands-free operation for clinical environments
- **Multiple TTS Options**: Fallback to enhanced espeak if natural voices unavailable 
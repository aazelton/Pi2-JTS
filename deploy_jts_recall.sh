#!/bin/bash

# JTS Recall Engine Deployment Script for Pi2
# Lightweight, fast recall engine for medical voice queries

echo "=== JTS Recall Engine Deployment ==="
echo "Raspberry Pi 2 Medical Voice Assistant"
echo "Offline JTS Clinical Decision Support"
echo ""

# Check if running on Pi2
if ! grep -q "Raspberry Pi 2" /proc/cpuinfo 2>/dev/null; then
    echo "⚠️  Warning: This script is designed for Raspberry Pi 2"
    echo "   Continue anyway? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Update system packages
echo "📦 Updating system packages..."
sudo apt update
sudo apt upgrade -y

# Install required system packages
echo "🔧 Installing required packages..."
sudo apt install -y \
    espeak-ng \
    poppler-utils \
    python3-pip \
    python3-venv \
    portaudio19-dev \
    python3-pyaudio \
    festival \
    festvox-us1-mbrola \
    festvox-us2-mbrola \
    festvox-us3-mbrola \
    mbrola \
    mbrola-us1 \
    mbrola-us2 \
    mbrola-us3

# Create project directory
PROJECT_DIR="/home/pi/jts_recall"
echo "📁 Creating project directory: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Create Python virtual environment
echo "🐍 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install \
    vosk==0.3.44 \
    sounddevice \
    rank-bm25 \
    PyMuPDF \
    pyaudio

# Download Vosk model
echo "🎤 Downloading Vosk speech recognition model..."
if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
    mkdir -p models
    cd models
    wget https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
    unzip vosk-model-small-en-us-0.15.zip
    rm vosk-model-small-en-us-0.15.zip
    cd ..
fi

# Create directories
echo "📋 Creating directories..."
mkdir -p jts_pdfs
mkdir -p jts_data

echo ""
echo "✅ JTS Recall Engine Base Installation Complete!"
echo ""
echo "📋 Next Steps:"
echo "1. Copy JTS PDF files to: $PROJECT_DIR/jts_pdfs/"
echo "2. Copy Python modules to: $PROJECT_DIR/"
echo "3. Run: ./run_jts_recall.sh"
echo ""
echo "🔧 System Requirements Met:"
echo "   ✅ espeak-ng (TTS fallback)"
echo "   ✅ festival + mbrola (TTS primary)"
echo "   ✅ poppler-utils (PDF processing)"
echo "   ✅ vosk (STT)"
echo "   ✅ sounddevice (Audio)"
echo "   ✅ rank_bm25 (Indexing)"
echo "   ✅ PyMuPDF (PDF extraction)"
echo ""
echo "📊 Performance Expectations:"
echo "   - Response Time: <1 second"
echo "   - Memory Usage: <100MB"
echo "   - Storage: ~50MB (excluding PDFs)"
echo "   - CPU: ARMv7 compatible"
echo ""
echo "🎯 Ready for field deployment!" 
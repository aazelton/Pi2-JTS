#!/bin/bash

# SPEC-1-MedicVoicePi2 Startup Script
# Raspberry Pi 2 Offline Medical Voice Assistant

echo "🎯 SPEC-1-MedicVoicePi2"
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

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "❌ Virtual environment not found. Please run deploy_pi2.sh first."
    exit 1
fi

# Set environment variables for Pi2 optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Check if required directories exist
if [ ! -d "jts_pdfs" ]; then
    echo "❌ Error: jts_pdfs directory not found!"
    echo "   Please ensure JTS PDF files are in the jts_pdfs directory."
    exit 1
fi

if [ ! -d "models/vosk-model-small-en-us-0.15" ]; then
    echo "❌ Error: Vosk model not found!"
    echo "   Please run deploy_pi2.sh to download the model."
    exit 1
fi

echo "🔧 SPEC-1 Architecture Components:"
echo "   ✅ PDF Text Extraction (PyMuPDF)"
echo "   ✅ Corpus Indexing (rank_bm25)"
echo "   ✅ Speech-to-Text (Vosk)"
echo "   ✅ Text Matching (BM25)"
echo "   ✅ Text-to-Speech (eSpeak NG)"
echo ""

echo "🎤 Starting SPEC-1-MedicVoicePi2..."
echo "📋 Speak medical queries for JTS guidance"
echo "🔇 Press Ctrl+C to exit"
echo ""

python spec1_medic_voice.py

echo ""
echo "👋 SPEC-1-MedicVoicePi2 stopped." 
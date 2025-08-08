#!/bin/bash

# Voice Agent Startup Script
# Updated modular architecture: PDF → Text Extraction → Indexing → Query Matching → TTS

echo "Starting Voice Agent System..."
echo "Architecture: PDF → Text Extraction → Indexing → Query Matching → TTS"

# Activate virtual environment
source venv/bin/activate

# Set environment variables for Pi2 optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Check if required directories exist
if [ ! -d "jts_pdfs" ]; then
    echo "Error: jts_pdfs directory not found!"
    echo "Please ensure JTS PDF files are in the jts_pdfs directory."
    exit 1
fi

# Create required directories
mkdir -p processed_data
mkdir -p text_index

echo "Initializing Voice Agent..."
python voice_agent.py

echo "Voice Agent stopped." 
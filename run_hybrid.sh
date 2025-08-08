#!/bin/bash

# Hybrid Voice Agent Startup Script
# Combines modular architecture with proven JTS decision engine

echo "Starting Hybrid Voice Agent System..."
echo "Architecture: PDF → Text Extraction → Indexing → JTS Decision Engine → TTS"

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

echo "Initializing Hybrid Voice Agent..."
python voice_agent_hybrid.py

echo "Hybrid Voice Agent stopped." 
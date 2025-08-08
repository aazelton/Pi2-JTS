#!/bin/bash
# JTS Clinical Assist Startup Script
# Voice-driven clinical decision making using Joint Trauma Services guidelines

echo "Starting JTS Clinical Assist System..."
echo "Voice-driven trauma care decision support"
echo ""

# Activate virtual environment
source venv/bin/activate

# Set environment variables for Pi2 optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Check if JTS data exists
if [ ! -d "jts_data" ] || [ ! -f "jts_data/metadata.json" ]; then
    echo "JTS data not found. Running setup..."
    python setup_jts.py
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please check the configuration."
        exit 1
    fi
fi

# Run the JTS system
echo "Launching JTS Clinical Assist..."
python main_jts.py 
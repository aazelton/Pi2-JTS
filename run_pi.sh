#!/bin/bash
# Raspberry Pi optimized startup script for P2 JTS Clinical Assist

echo "Starting P2 JTS Clinical Assist (Pi Optimized)..."
echo "Using optimized voice settings for Raspberry Pi"
echo "Make sure your microphone is connected and working."
echo ""

# Activate virtual environment and run the application
source venv/bin/activate

# Set environment variables for Pi optimization
export PYTHONOPTIMIZE=1
export PYTHONDONTWRITEBYTECODE=1

# Run with Pi-optimized TTS
python main_pi.py 
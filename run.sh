#!/bin/bash
# Startup script for P2 JTS Clinical Assist

echo "Starting P2 JTS Clinical Assist..."
echo "Make sure your microphone is connected and working."
echo ""

# Activate virtual environment and run the application
source venv/bin/activate
python main.py 
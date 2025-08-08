# JTS Clinical Assist System

## Overview

The JTS (Joint Trauma Services) Clinical Assist System is a voice-driven clinical decision support tool designed for trauma care professionals. It processes approximately 100 JTS PDF guidelines (~100MB) and provides real-time, voice-activated access to trauma care protocols and recommendations.

## Features

### 🎤 Voice-Driven Interface
- **Natural Voice Input**: Uses Vosk speech recognition for hands-free operation
- **Natural Voice Output**: Kathy voice (macOS) or enhanced espeak for clear communication
- **Conversation History**: Tracks clinical queries and responses for documentation

### 📚 JTS Guidelines Integration
- **PDF Processing**: Automatically extracts and categorizes JTS guidelines
- **Smart Categorization**: Organizes content into clinical categories (airway, circulation, neurological, etc.)
- **Intelligent Search**: Finds relevant guidelines based on voice queries
- **Confidence Scoring**: Indicates reliability of recommendations

### 🏥 Clinical Decision Support
- **Real-time Recommendations**: Provides immediate clinical guidance
- **Multiple Guidelines**: Cross-references multiple JTS documents
- **Context-Aware Responses**: Tailors responses to clinical scenarios
- **Emergency Protocols**: Prioritizes critical care information

### 💾 Pi2 Optimization
- **Storage Efficient**: Optimized for 128GB SD card
- **Memory Management**: Efficient loading and caching of guidelines
- **Performance Tuned**: Optimized for Raspberry Pi 2 hardware

## System Requirements

### Hardware
- **Raspberry Pi 2** (or compatible)
- **128GB SD Card** (minimum 10GB free space)
- **Microphone** (USB or built-in)
- **Speakers** (for voice output)

### Software
- **Python 3.8+**
- **macOS/Linux** (for development and testing)
- **Raspberry Pi OS** (for deployment)

## Installation

### 1. Clone and Setup
```bash
git clone <repository-url>
cd Pi2-JTS
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Download Speech Recognition Model
```bash
mkdir -p models
cd models
curl -L -o vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip
unzip vosk-model-small-en-us-0.15.zip
rm vosk-model-small-en-us-0.15.zip
cd ..
```

### 3. Add JTS PDF Files
```bash
mkdir jts_pdfs
# Copy your JTS PDF files to the jts_pdfs directory
```

### 4. Run Setup
```bash
python setup_jts.py
```

## Usage

### Quick Start
```bash
./run_jts.sh
```

### Manual Start
```bash
source venv/bin/activate
python main_jts.py
```

### Voice Commands
- **Clinical Questions**: "How to assess airway in trauma?"
- **Treatment Queries**: "What's the treatment for hemorrhagic shock?"
- **Medication Info**: "What medications for pain management?"
- **System Commands**:
  - "summary" - Get conversation summary
  - "categories" - List available guideline categories
  - "exit" - Quit the system

## System Architecture

### Core Components

1. **JTS PDF Processor** (`jts_processor.py`)
   - Extracts text from PDF files
   - Categorizes content by clinical domain
   - Creates searchable JSON database

2. **Decision Engine** (`jts_decision_engine.py`)
   - Processes voice queries
   - Searches relevant guidelines
   - Generates clinical recommendations

3. **Voice Interface** (`main_jts.py`)
   - Manages speech recognition
   - Handles voice output
   - Coordinates user interaction

4. **TTS Utilities** (`tts_utils.py`)
   - Natural voice synthesis
   - Multiple voice options
   - Fallback mechanisms

### Data Flow
```
Voice Input → Speech Recognition → Query Processing → 
Guideline Search → Response Generation → Voice Output
```

## File Structure
```
Pi2-JTS/
├── main_jts.py              # Main JTS application
├── jts_processor.py         # PDF processing engine
├── jts_decision_engine.py   # Clinical decision engine
├── tts_utils.py            # Text-to-speech utilities
├── setup_jts.py            # System setup script
├── run_jts.sh              # Startup script
├── requirements.txt        # Python dependencies
├── jts_pdfs/              # Input PDF files
├── jts_data/              # Processed guideline data
├── models/                # Speech recognition models
└── venv/                  # Virtual environment
```

## Configuration

### Voice Settings
- **Primary Voice**: Kathy (natural, professional)
- **Fallback Voices**: Samantha, Fred, Flo, Ralph
- **Speed**: 140 words per minute (optimal for clinical use)

### Performance Settings
- **Memory Usage**: Optimized for Pi2 constraints
- **Search Results**: Top 5 most relevant guidelines
- **Response Length**: Truncated for voice output

## Troubleshooting

### Common Issues

1. **No Voice Output**
   - Check microphone permissions
   - Verify espeak installation
   - Test with `say -v Kathy "test"`

2. **Speech Recognition Issues**
   - Ensure Vosk model is downloaded
   - Check microphone connection
   - Verify audio device settings

3. **PDF Processing Errors**
   - Check PDF file integrity
   - Ensure sufficient disk space
   - Verify PyPDF2 installation

4. **Performance Issues**
   - Close unnecessary applications
   - Check available memory
   - Consider reducing guideline set

### Logs and Debugging
```bash
# Enable debug logging
export PYTHONPATH=.
python -c "import logging; logging.basicConfig(level=logging.DEBUG)"
```

## Clinical Use Cases

### Emergency Department
- **Rapid Assessment**: Voice queries for trauma protocols
- **Treatment Guidance**: Real-time medication and procedure recommendations
- **Documentation**: Automatic conversation logging

### Field Medicine
- **Portable Decision Support**: Pi2-based mobile system
- **Offline Operation**: No internet required after setup
- **Battery Efficient**: Optimized for extended use

### Training and Education
- **Protocol Review**: Voice-activated guideline access
- **Case Studies**: Interactive clinical scenarios
- **Competency Assessment**: Track guideline usage

## Development

### Adding New Guidelines
1. Place PDF files in `jts_pdfs/`
2. Run `python jts_processor.py`
3. Restart the system

### Customizing Voice Responses
- Edit `jts_decision_engine.py` response generation
- Modify voice settings in `tts_utils.py`
- Add new voice options

### Extending Categories
- Update categories in `jts_processor.py`
- Add new decision patterns in `jts_decision_engine.py`
- Test with relevant queries

## Performance Metrics

### Storage Requirements
- **Vosk Model**: ~40MB
- **JTS Guidelines**: ~100MB (processed)
- **System Files**: ~50MB
- **Total**: ~190MB

### Memory Usage
- **Speech Recognition**: ~100MB
- **Guideline Database**: ~50MB
- **System Overhead**: ~50MB
- **Total**: ~200MB

### Response Time
- **Voice Recognition**: <2 seconds
- **Guideline Search**: <1 second
- **Voice Synthesis**: <3 seconds
- **Total**: <6 seconds

## Security and Privacy

### Data Protection
- **Local Processing**: All data processed locally
- **No Cloud Dependencies**: Offline operation
- **Conversation Logging**: Optional local storage

### Clinical Compliance
- **Guideline Accuracy**: Direct from JTS sources
- **Audit Trail**: Conversation history for documentation
- **Version Control**: Track guideline updates

## Support and Maintenance

### Regular Maintenance
- **Guideline Updates**: Process new JTS PDFs
- **System Updates**: Update Python packages
- **Performance Monitoring**: Check system resources

### Backup and Recovery
- **Data Backup**: Regular backup of `jts_data/`
- **Configuration Backup**: Save system settings
- **Disaster Recovery**: Reinstall from backup

## License and Compliance

This system is designed for clinical use and should be used in accordance with:
- **JTS Guidelines**: Respect original guideline licensing
- **Clinical Standards**: Follow institutional protocols
- **Privacy Regulations**: Comply with HIPAA and local regulations

## Contact and Support

For technical support or clinical questions:
- **Documentation**: Check this README and code comments
- **Issues**: Review troubleshooting section
- **Updates**: Monitor repository for updates

---

**Disclaimer**: This system is a decision support tool and should not replace clinical judgment. Always verify recommendations against current clinical standards and institutional protocols. 
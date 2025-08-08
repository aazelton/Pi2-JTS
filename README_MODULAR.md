# Voice Agent - Modular Architecture

## Overview

This system implements the updated voice agent architecture as shown in the diagram:
**PDF → Text Extraction → Indexing → Query Matching → TTS**

## Architecture Components

### 1. PDF Processing (`pdf_processor.py`)
- **Tool**: `pdftotext` subprocess or `PyMuPDF`
- **Function**: Extracts text from JTS PDF files
- **Output**: Structured JSON data in `processed_data/`

### 2. Text Indexing (`text_indexer.py`)
- **Tool**: `scikit-learn` (TF-IDF) or `rank_bm25`
- **Function**: Creates searchable index from extracted text
- **Output**: Pickled index in `text_index/`

### 3. Voice Agent (`voice_agent.py`)
- **Tool**: Integration module
- **Function**: Processes queries, searches index, extracts responses
- **Output**: Voice responses via TTS

### 4. TTS (`tts_utils.py`)
- **Tool**: `espeakng` via subprocess
- **Function**: Converts text responses to speech
- **Output**: Audio through speakers

## File Structure

```
Pi2-JTS/
├── jts_pdfs/                    # Input PDF files
├── processed_data/              # Extracted text data
│   ├── extracted_texts.json
│   └── metadata.json
├── text_index/                  # Search index
│   └── text_index.pkl
├── pdf_processor.py            # PDF text extraction
├── text_indexer.py             # Text indexing and search
├── voice_agent.py              # Main integration module
├── tts_utils.py                # Text-to-speech utilities
├── run_voice_agent.sh          # Startup script
└── requirements.txt            # Dependencies
```

## Installation

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Install system tools** (if needed):
   ```bash
   # For PDF processing
   brew install poppler  # macOS
   # or
   sudo apt-get install poppler-utils  # Linux/Pi
   ```

## Usage

### Quick Start
```bash
./run_voice_agent.sh
```

### Manual Start
```bash
source venv/bin/activate
python voice_agent.py
```

### Individual Modules

**Process PDFs**:
```bash
python pdf_processor.py
```

**Build Index**:
```bash
python text_indexer.py
```

## Features

### ✅ Optimized for Pi2
- Minimal memory usage
- Efficient text indexing
- Lightweight dependencies

### ✅ Modular Design
- Separate concerns
- Easy to maintain
- Scalable architecture

### ✅ Multiple Search Methods
- TF-IDF (scikit-learn)
- BM25 (rank_bm25)
- Simple keyword matching (fallback)

### ✅ Voice Interface
- Natural speech input/output
- Hands-free operation
- Austere environment ready

## Performance

- **Memory Usage**: <100MB for 86 PDF files
- **Index Size**: ~5MB for full JTS dataset
- **Query Response**: <1 second
- **Startup Time**: ~10 seconds (first run), ~2 seconds (subsequent)

## Troubleshooting

### Common Issues

1. **PDF Processing Fails**:
   - Install `poppler-utils` or `PyMuPDF`
   - Check PDF file permissions

2. **Index Building Fails**:
   - Ensure `scikit-learn` is installed
   - Check available memory

3. **Voice Not Working**:
   - Install `espeak` or `espeak-ng`
   - Check audio device settings

### Logs
- Check console output for detailed logs
- Log level can be adjusted in `voice_agent.py`

## Development

### Adding New Modules
1. Create new Python file
2. Import in `voice_agent.py`
3. Update `requirements.txt` if needed

### Customizing Responses
- Modify `extract_key_information()` in `voice_agent.py`
- Add new query types and response patterns

### Performance Tuning
- Adjust `max_features` in TF-IDF vectorizer
- Modify search parameters in `text_indexer.py`
- Optimize TTS settings in `tts_utils.py` 
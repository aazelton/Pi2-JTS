#!/usr/bin/env python3
"""
SPEC-1-MedicVoicePi2 Main Application
Raspberry Pi 2 Offline Medical Voice Assistant
Following exact SPEC-1 architecture and requirements
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import logging

# SPEC-1 Required Libraries
from vosk import Model, KaldiRecognizer
import sounddevice as sd
from rank_bm25 import BM25Okapi
import fitz  # PyMuPDF

logger = logging.getLogger(__name__)

class SPEC1MedicVoice:
    """
    SPEC-1-MedicVoicePi2 Implementation
    Follows exact architecture: Medic → Mic → VoskSTT → Text → Index → Match → eSpeak
    """
    
    def __init__(self, model_path: str = "models/vosk-model-small-en-us-0.15"):
        self.model_path = model_path
        self.model = None
        self.recognizer = None
        self.bm25_index = None
        self.corpus = []
        self.corpus_texts = []
        
        # SPEC-1 Configuration
        self.sample_rate = 16000
        self.chunk_size = 8000
        
    def initialize(self) -> bool:
        """Initialize SPEC-1 system components"""
        try:
            logger.info("Initializing SPEC-1-MedicVoicePi2...")
            
            # 1. Load Vosk STT model (SPEC-1 requirement)
            logger.info("Loading Vosk STT model...")
            if not os.path.exists(self.model_path):
                raise FileNotFoundError(f"Vosk model not found at {self.model_path}")
            
            self.model = Model(self.model_path)
            self.recognizer = KaldiRecognizer(self.model, self.sample_rate)
            
            # 2. Load JTS corpus and build BM25 index
            logger.info("Loading JTS corpus and building BM25 index...")
            self.load_jts_corpus()
            self.build_bm25_index()
            
            logger.info("SPEC-1-MedicVoicePi2 initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SPEC-1 system: {e}")
            return False
    
    def load_jts_corpus(self):
        """Load JTS PDF corpus (SPEC-1 requirement: PDF text extraction)"""
        jts_dir = Path("jts_pdfs")
        if not jts_dir.exists():
            raise FileNotFoundError("JTS PDFs directory not found")
        
        pdf_files = list(jts_dir.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} JTS PDF files")
        
        for pdf_file in pdf_files:
            try:
                # Extract text using PyMuPDF (SPEC-1 requirement)
                with fitz.open(pdf_file) as doc:
                    text = "\n".join(page.get_text() for page in doc)
                
                # Split into paragraphs (SPEC-1 requirement: simple tokenization)
                paragraphs = [para.strip() for para in text.split('\n') if len(para.strip()) > 20]
                
                for para in paragraphs:
                    self.corpus_texts.append(para)
                    # Tokenize for BM25 (SPEC-1 requirement: simple tokenization)
                    tokens = para.lower().split()
                    self.corpus.append(tokens)
                
            except Exception as e:
                logger.warning(f"Failed to process {pdf_file}: {e}")
        
        logger.info(f"Loaded {len(self.corpus)} corpus entries")
    
    def build_bm25_index(self):
        """Build BM25 index (SPEC-1 requirement: rank_bm25)"""
        if not self.corpus:
            raise ValueError("No corpus loaded")
        
        # Build BM25 index (SPEC-1 requirement)
        self.bm25_index = BM25Okapi(self.corpus)
        logger.info("BM25 index built successfully")
    
    def recognize_speech(self) -> str:
        """Recognize speech using Vosk STT (SPEC-1 requirement)"""
        logger.info("Listening for speech input...")
        
        def audio_callback(indata, frames, time, status):
            if status:
                logger.warning(f"Audio callback status: {status}")
            if self.recognizer.AcceptWaveform(indata.tobytes()):
                result = json.loads(self.recognizer.Result())
                if result.get('text'):
                    return result['text']
            return None
        
        try:
            with sd.InputStream(callback=audio_callback,
                              channels=1,
                              samplerate=self.sample_rate,
                              blocksize=self.chunk_size):
                print("🎤 Speak your medical query (Ctrl+C to stop)...")
                while True:
                    sd.sleep(100)  # Check every 100ms
                    
        except KeyboardInterrupt:
            # Get final result
            result = json.loads(self.recognizer.FinalResult())
            return result.get('text', '')
    
    def match_query(self, query: str, top_n: int = 1) -> List[str]:
        """Match query against BM25 index (SPEC-1 requirement)"""
        if not self.bm25_index:
            raise ValueError("BM25 index not built")
        
        # Tokenize query (SPEC-1 requirement: simple tokenization)
        query_tokens = query.lower().split()
        
        # Get top N results (SPEC-1 requirement)
        top_indices = self.bm25_index.get_top_n(query_tokens, self.corpus, n=top_n)
        
        # Convert back to text
        results = []
        for tokens in top_indices:
            text = ' '.join(tokens)
            results.append(text)
        
        return results
    
    def speak_response(self, text: str):
        """Speak response using eSpeak NG (SPEC-1 requirement)"""
        try:
            # SPEC-1 requirement: subprocess.run(["espeak-ng", text])
            subprocess.run(["espeak-ng", text], check=True)
        except subprocess.CalledProcessError as e:
            logger.error(f"eSpeak NG failed: {e}")
            print(f"Response: {text}")
        except FileNotFoundError:
            logger.error("eSpeak NG not found")
            print(f"Response: {text}")
    
    def run_interactive_mode(self):
        """Run interactive SPEC-1 medical voice assistant"""
        if not self.model or not self.bm25_index:
            print("System not initialized. Please run initialize() first.")
            return
        
        print("🎯 SPEC-1-MedicVoicePi2 Ready!")
        print("📋 Speak medical queries for JTS guidance")
        print("🔇 Press Ctrl+C to exit")
        print("")
        
        while True:
            try:
                # SPEC-1 Architecture Flow:
                # Medic → Mic → VoskSTT → Text → Index → Match → eSpeak
                
                # 1. Recognize speech
                query = self.recognize_speech()
                
                if not query.strip():
                    continue
                
                print(f"🎤 Recognized: {query}")
                
                # 2. Match against BM25 index
                results = self.match_query(query, top_n=1)
                
                if not results:
                    response = "I couldn't find relevant JTS guidance for that query."
                else:
                    response = results[0]
                
                # 3. Speak response
                print(f"📋 Response: {response[:100]}...")
                self.speak_response(response)
                
            except KeyboardInterrupt:
                print("\n👋 SPEC-1-MedicVoicePi2 stopped.")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print("I encountered an error. Please try again.")

def main():
    """SPEC-1-MedicVoicePi2 Main Entry Point"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create SPEC-1 system
    medic_voice = SPEC1MedicVoice()
    
    # Initialize system
    if not medic_voice.initialize():
        print("❌ Failed to initialize SPEC-1-MedicVoicePi2. Exiting.")
        return
    
    # Run interactive mode
    medic_voice.run_interactive_mode()

if __name__ == "__main__":
    main() 
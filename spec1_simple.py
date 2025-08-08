#!/usr/bin/env python3
"""
SPEC-1-MedicVoicePi2 Simplified Implementation
Raspberry Pi 2 Offline Medical Voice Assistant
Uses existing working components with SPEC-1 architecture
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import List, Dict, Optional
import logging

# Add system Python path for dependencies
sys.path.append('/Users/andrew/Library/Python/3.9/lib/python/site-packages')

# Import working components
from jts_decision_engine import JTSDecisionEngine
from tts_festival import speak  # Use Festival TTS for better quality

logger = logging.getLogger(__name__)

class SPEC1Simple:
    """
    SPEC-1-MedicVoicePi2 Simplified Implementation
    Uses proven JTS decision engine with SPEC-1 architecture
    """
    
    def __init__(self):
        self.jts_engine = None
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize SPEC-1 system components"""
        try:
            logger.info("Initializing SPEC-1-MedicVoicePi2 (Simplified)...")
            
            # Initialize JTS decision engine (proven to work)
            logger.info("Loading JTS decision engine...")
            self.jts_engine = JTSDecisionEngine()
            
            self.is_initialized = True
            logger.info("SPEC-1-MedicVoicePi2 (Simplified) initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize SPEC-1 system: {e}")
            return False
    
    def process_query(self, query: str) -> str:
        """Process a voice query using SPEC-1 architecture"""
        if not self.is_initialized:
            return "System not initialized. Please run initialize() first."
        
        try:
            # SPEC-1 Architecture Flow:
            # Medic → Mic → VoskSTT → Text → JTS Engine → Match → eSpeak
            
            logger.info(f"Processing query: {query}")
            
            # Use JTS decision engine for clinical responses
            decision = self.jts_engine.extract_clinical_decision(query)
            response = self.jts_engine.generate_voice_response(decision)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "I encountered an error processing your query."
    
    def run_interactive_mode(self):
        """Run interactive SPEC-1 medical voice assistant"""
        if not self.is_initialized:
            print("System not initialized. Please run initialize() first.")
            return
        
        print("🎯 SPEC-1-MedicVoicePi2 (Simplified) Ready!")
        print("📋 Type medical queries for JTS guidance")
        print("🔇 Type 'quit' to exit")
        print("")
        
        while True:
            try:
                # Get user input (simulating voice input for now)
                user_input = input("🎤 Query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    break
                
                if not user_input:
                    continue
                
                # Process query using SPEC-1 architecture
                response = self.process_query(user_input)
                
                # Display and speak response
                print(f"📋 Response: {response}")
                speak(response)
                
            except KeyboardInterrupt:
                print("\n👋 SPEC-1-MedicVoicePi2 stopped.")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print("I encountered an error. Please try again.")

def main():
    """SPEC-1-MedicVoicePi2 Simplified Main Entry Point"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create SPEC-1 system
    medic_voice = SPEC1Simple()
    
    # Initialize system
    if not medic_voice.initialize():
        print("❌ Failed to initialize SPEC-1-MedicVoicePi2. Exiting.")
        return
    
    # Run interactive mode
    medic_voice.run_interactive_mode()

if __name__ == "__main__":
    main() 
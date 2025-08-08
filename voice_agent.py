#!/usr/bin/env python3
"""
Voice Agent Module
Main integration module that combines PDF processing, text indexing, and voice interface
Follows the updated architecture: PDF → Text Extraction → Indexing → Query Matching → TTS
"""

import logging
import sys
from pathlib import Path
from typing import Dict, List, Optional

# Import our modules
from pdf_processor import PDFProcessor
from text_indexer import TextIndexer
from tts_utils import speak

logger = logging.getLogger(__name__)

class VoiceAgent:
    def __init__(self):
        self.pdf_processor = PDFProcessor()
        self.text_indexer = TextIndexer()
        self.is_initialized = False
        
    def initialize(self) -> bool:
        """Initialize the voice agent system"""
        try:
            logger.info("Initializing Voice Agent...")
            
            # Check if processed data exists
            processed_data_file = Path("processed_data/extracted_texts.json")
            if not processed_data_file.exists():
                logger.info("Processed data not found. Processing PDFs...")
                self.pdf_processor.process_pdf_directory()
            
            # Check if index exists
            index_file = Path("text_index/text_index.pkl")
            if not index_file.exists():
                logger.info("Text index not found. Building index...")
                self.text_indexer.build_index("tfidf")
            else:
                logger.info("Loading existing text index...")
                self.text_indexer.load_index()
            
            self.is_initialized = True
            logger.info("Voice Agent initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Voice Agent: {e}")
            return False
    
    def process_query(self, query: str) -> str:
        """Process a voice query and return response"""
        if not self.is_initialized:
            return "System not initialized. Please run initialize() first."
        
        try:
            # Search for relevant content
            results = self.text_indexer.search(query, top_k=3)
            
            if not results:
                return "I couldn't find relevant information for that query."
            
            # Get the best response
            best_result = results[0]
            
            # Extract key information from the content
            response = self.extract_key_information(best_result['content'], query)
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing query: {e}")
            return "I encountered an error processing your query."
    
    def extract_key_information(self, content: str, query: str) -> str:
        """Extract key information from content based on query type"""
        query_lower = query.lower()
        content_lower = content.lower()
        
        # Medication dosing queries
        if any(med in query_lower for med in ['ketamine', 'morphine', 'fentanyl', 'dose', 'dosage']):
            return self.extract_medication_dosage(content, query)
        
        # Airway queries
        elif 'airway' in query_lower:
            return self.extract_airway_guidance(content, query)
        
        # General trauma queries
        elif any(word in query_lower for word in ['trauma', 'injury', 'emergency']):
            return self.extract_trauma_guidance(content, query)
        
        # Default: return first 200 characters
        else:
            return content[:200] + "..." if len(content) > 200 else content
    
    def extract_medication_dosage(self, content: str, query: str) -> str:
        """Extract medication dosage information"""
        import re
        
        # Look for dosage patterns
        dosage_patterns = [
            r'(\d+(?:\.\d+)?)\s*(?:mg|mg/kg|mg/kg/dose)',
            r'(\d+(?:\.\d+)?)\s*to\s*(\d+(?:\.\d+)?)\s*(?:mg|mg/kg)',
            r'(\d+(?:\.\d+)?)\s*mg/kg'
        ]
        
        for pattern in dosage_patterns:
            matches = re.findall(pattern, content)
            if matches:
                # Return the first dosage found
                if isinstance(matches[0], tuple):
                    min_dose, max_dose = matches[0][0], matches[0][1] if len(matches[0]) > 1 else matches[0][0]
                    return f"{min_dose}-{max_dose}mg/kg"
                else:
                    dose = matches[0]
                    return f"{dose}mg/kg"
        
        # If no specific dosage found, return general guidance
        return "Consult JTS guidelines for specific dosing protocols."
    
    def extract_airway_guidance(self, content: str, query: str) -> str:
        """Extract airway management guidance"""
        # Look for key airway terms
        airway_keywords = ['assess', 'intubate', 'ventilate', 'oxygenate', 'airway']
        
        # Find sentences with airway keywords
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in airway_keywords):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Return the most relevant sentence
            return relevant_sentences[0][:150] + "..." if len(relevant_sentences[0]) > 150 else relevant_sentences[0]
        
        return "Assess airway patency and provide appropriate intervention based on clinical findings."
    
    def extract_trauma_guidance(self, content: str, query: str) -> str:
        """Extract trauma management guidance"""
        # Look for key trauma terms
        trauma_keywords = ['assess', 'control', 'manage', 'treat', 'resuscitate']
        
        # Find sentences with trauma keywords
        sentences = content.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in trauma_keywords):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            # Return the most relevant sentence
            return relevant_sentences[0][:150] + "..." if len(relevant_sentences[0]) > 150 else relevant_sentences[0]
        
        return "Follow standard trauma protocols and consult JTS guidelines for specific management."
    
    def run_interactive_mode(self):
        """Run interactive voice mode"""
        if not self.is_initialized:
            print("System not initialized. Please run initialize() first.")
            return
        
        print("Voice Agent ready! Speak your query or type 'quit' to exit.")
        speak("Voice Agent ready. How can I help you?")
        
        while True:
            try:
                # Get user input (voice or text)
                user_input = input("Query: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'stop']:
                    break
                
                if not user_input:
                    continue
                
                # Process query
                response = self.process_query(user_input)
                
                # Display and speak response
                print(f"Response: {response}")
                speak(response)
                
            except KeyboardInterrupt:
                print("\nExiting...")
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                print("I encountered an error. Please try again.")

def main():
    """Main entry point"""
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create voice agent
    agent = VoiceAgent()
    
    # Initialize system
    if not agent.initialize():
        print("Failed to initialize Voice Agent. Exiting.")
        return
    
    # Run interactive mode
    agent.run_interactive_mode()

if __name__ == "__main__":
    main() 
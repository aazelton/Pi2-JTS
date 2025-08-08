#!/usr/bin/env python3
"""
P2 JTS Clinical Assist - Enhanced Version
Voice-driven clinical decision making using Joint Trauma Services guidelines
Optimized for Pi2 with 128GB storage
"""

from vosk import Model, KaldiRecognizer
import pyaudio
import json
import subprocess
from tts_utils import speak, set_voice
from jts_decision_engine import VoiceDrivenJTS
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JTSClinicalAssist:
    def __init__(self):
        self.model = None
        self.jts_engine = None
        self.is_running = False
        
    def initialize_system(self):
        """Initialize the JTS clinical assistance system"""
        print("Initializing JTS Clinical Assist System...")
        
        # Load speech recognition model
        print("Loading speech recognition model...")
        try:
            self.model = Model("models/vosk-model-small-en-us-0.15")
            print("✓ Speech recognition model loaded")
        except Exception as e:
            print(f"❌ Error loading speech model: {e}")
            return False
        
        # Initialize JTS decision engine
        print("Loading JTS guidelines...")
        try:
            self.jts_engine = VoiceDrivenJTS()
            print("✓ JTS decision engine initialized")
        except Exception as e:
            print(f"❌ Error loading JTS engine: {e}")
            return False
        
        # Set voice preference
        set_voice("en-us")
        
        print("System initialization complete!")
        return True
    
    def listen_for_query(self):
        """Listen for voice query using Vosk"""
        rec = KaldiRecognizer(self.model, 16000)
        mic = pyaudio.PyAudio().open(
            format=pyaudio.paInt16,
            channels=1,
            rate=16000,
            input=True,
            frames_per_buffer=8192
        )
        
        mic.start_stream()
        print("Listening for your query...")
        
        while True:
            data = mic.read(4096, exception_on_overflow=False)
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "").strip()
                if text:
                    return text
        
        mic.stop_stream()
        mic.close()
    
    def process_clinical_query(self, query: str):
        """Process clinical query and provide voice response"""
        print(f"Processing query: {query}")
        
        # Process through JTS engine
        result = self.jts_engine.process_voice_query(query)
        
        # Speak the response
        response = result['response']
        print(f"Response: {response}")
        speak(response)
        
        return result
    
    def run_interactive_mode(self):
        """Run interactive voice-driven clinical assistance"""
        print("\n" + "="*60)
        print("JTS Clinical Assist - Voice-Driven Mode")
        print("="*60)
        print("Available commands:")
        print("- Ask clinical questions (e.g., 'How to assess airway?')")
        print("- Say 'summary' for conversation summary")
        print("- Say 'categories' for available guideline categories")
        print("- Say 'exit' to quit")
        print("="*60)
        
        self.is_running = True
        
        while self.is_running:
            try:
                # Listen for query
                query = self.listen_for_query()
                
                if not query:
                    continue
                
                print(f"\nYou said: {query}")
                
                # Handle special commands
                if query.lower() in ['exit', 'quit', 'stop']:
                    speak("Exiting JTS Clinical Assist. Thank you for using the system.")
                    self.is_running = False
                    break
                
                elif query.lower() == 'summary':
                    summary = self.jts_engine.get_conversation_summary()
                    print("Conversation Summary:")
                    print(summary)
                    speak("I've displayed the conversation summary on screen.")
                    continue
                
                elif query.lower() == 'categories':
                    categories = self.jts_engine.decision_engine.get_available_categories()
                    category_list = ", ".join(categories)
                    print(f"Available categories: {category_list}")
                    speak(f"Available guideline categories are: {category_list}")
                    continue
                
                # Process clinical query
                result = self.process_clinical_query(query)
                
                # Ask if user wants more information
                if result['confidence'] and len(result['decision']['relevant_guidelines']) > 1:
                    speak("Would you like more specific information about any of these guidelines?")
                
            except KeyboardInterrupt:
                print("\nInterrupted by user")
                speak("System interrupted. Exiting.")
                self.is_running = False
                break
            except Exception as e:
                logger.error(f"Error in interactive mode: {e}")
                speak("I encountered an error. Please try again.")
    
    def run_demo_mode(self):
        """Run demo mode with predefined queries"""
        print("\nRunning JTS Clinical Assist Demo Mode...")
        
        demo_queries = [
            "I have a badly burned patient, and need to give ketamine for pain, hes 80kg",
            "airway compromise help",
            "hemorrhage control",
            "burn assessment"
        ]
        
        for query in demo_queries:
            print(f"\nDemo Query: {query}")
            speak(f"Demo query: {query}")
            
            # Process query
            result = self.process_clinical_query(query)
            
            # Wait for user input to continue
            input("Press Enter to continue to next demo query...")
        
        print("Demo completed!")

def main():
    """Main application entry point"""
    app = JTSClinicalAssist()
    
    # Initialize system
    if not app.initialize_system():
        print("Failed to initialize system. Exiting.")
        return
    
    # Check if JTS data is available
    if not app.jts_engine.decision_engine.guidelines:
        print("No JTS guidelines found. Please process PDF files first.")
        print("Run: python jts_processor.py")
        return
    
    # Show available categories
    categories = app.jts_engine.decision_engine.get_available_categories()
    print(f"\nLoaded {len(categories)} guideline categories:")
    for category in categories:
        summary = app.jts_engine.decision_engine.get_category_summary(category)
        print(f"- {category}: {summary.get('file_count', 0)} files, {summary.get('total_size_mb', 0):.1f}MB")
    
    # Ask user for mode
    print("\nSelect mode:")
    print("1. Interactive voice mode")
    print("2. Demo mode")
    
    try:
        choice = input("Enter choice (1 or 2): ").strip()
        
        if choice == "1":
            app.run_interactive_mode()
        elif choice == "2":
            app.run_demo_mode()
        else:
            print("Invalid choice. Running interactive mode.")
            app.run_interactive_mode()
            
    except KeyboardInterrupt:
        print("\nExiting...")
        speak("Goodbye!")

if __name__ == "__main__":
    main() 
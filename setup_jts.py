#!/usr/bin/env python3
"""
JTS System Setup Script
Helps set up the Joint Trauma Services clinical decision system
"""

import os
import sys
from pathlib import Path
import subprocess

def check_dependencies():
    """Check if required dependencies are installed"""
    print("Checking dependencies...")
    
    required_packages = ['vosk', 'pyaudio', 'PyPDF2']
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - missing")
    
    if missing_packages:
        print(f"\nMissing packages: {', '.join(missing_packages)}")
        print("Please install missing packages:")
        print(f"pip install {' '.join(missing_packages)}")
        return False
    
    return True

def check_system_requirements():
    """Check system requirements for Pi2"""
    print("\nChecking system requirements...")
    
    # Check available disk space (simplified)
    try:
        import shutil
        total, used, free = shutil.disk_usage("/")
        free_gb = free / (1024**3)
        print(f"✓ Available disk space: {free_gb:.1f}GB")
        
        if free_gb < 10:
            print("⚠️  Warning: Less than 10GB free space available")
            return False
    except:
        print("⚠️  Could not check disk space")
    
    # Check Python version
    python_version = sys.version_info
    print(f"✓ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    if python_version < (3, 8):
        print("❌ Python 3.8 or higher required")
        return False
    
    return True

def setup_directories():
    """Create necessary directories"""
    print("\nSetting up directories...")
    
    directories = [
        "jts_pdfs",
        "jts_data", 
        "models"
    ]
    
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Created directory: {directory}")

def check_vosk_model():
    """Check if Vosk model is available"""
    print("\nChecking Vosk speech recognition model...")
    
    model_path = Path("models/vosk-model-small-en-us-0.15")
    if model_path.exists():
        print("✓ Vosk model found")
        return True
    else:
        print("❌ Vosk model not found")
        print("Please download the model:")
        print("cd models")
        print("curl -L -o vosk-model-small-en-us-0.15.zip https://alphacephei.com/vosk/models/vosk-model-small-en-us-0.15.zip")
        print("unzip vosk-model-small-en-us-0.15.zip")
        print("rm vosk-model-small-en-us-0.15.zip")
        return False

def check_jts_pdfs():
    """Check if JTS PDFs are available"""
    print("\nChecking JTS PDF files...")
    
    pdf_dir = Path("jts_pdfs")
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if pdf_files:
        print(f"✓ Found {len(pdf_files)} PDF files")
        total_size = sum(f.stat().st_size for f in pdf_files)
        print(f"✓ Total size: {total_size / (1024*1024):.1f}MB")
        return True
    else:
        print("❌ No PDF files found in jts_pdfs directory")
        print("Please place your JTS PDF files in the jts_pdfs directory")
        return False

def process_jts_pdfs():
    """Process JTS PDF files"""
    print("\nProcessing JTS PDF files...")
    
    try:
        from jts_processor import JTSPDFProcessor
        processor = JTSPDFProcessor()
        processor.process_pdf_directory()
        print("✓ PDF processing completed")
        return True
    except Exception as e:
        print(f"❌ Error processing PDFs: {e}")
        return False

def test_system():
    """Test the JTS system"""
    print("\nTesting JTS system...")
    
    try:
        from jts_decision_engine import VoiceDrivenJTS
        jts = VoiceDrivenJTS()
        
        # Test a simple query
        result = jts.process_voice_query("How to assess airway?")
        print(f"✓ System test successful - Confidence: {result['confidence']}")
        return True
    except Exception as e:
        print(f"❌ System test failed: {e}")
        return False

def main():
    """Main setup function"""
    print("JTS Clinical Assist System Setup")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        print("\nPlease install missing dependencies and run setup again.")
        return
    
    # Check system requirements
    if not check_system_requirements():
        print("\nSystem requirements not met. Please address issues and run setup again.")
        return
    
    # Setup directories
    setup_directories()
    
    # Check Vosk model
    if not check_vosk_model():
        print("\nPlease download the Vosk model and run setup again.")
        return
    
    # Check JTS PDFs
    if not check_jts_pdfs():
        print("\nPlease add JTS PDF files and run setup again.")
        return
    
    # Process PDFs
    if not process_jts_pdfs():
        print("\nPDF processing failed. Please check your PDF files.")
        return
    
    # Test system
    if not test_system():
        print("\nSystem test failed. Please check the configuration.")
        return
    
    print("\n" + "=" * 40)
    print("✅ JTS System Setup Complete!")
    print("=" * 40)
    print("You can now run the system with:")
    print("python main_jts.py")
    print("\nOr use the startup script:")
    print("./run_jts.sh")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
JTS PDF Download Helper
Assists in downloading JTS PDF files from various sources
"""

import os
import requests
import urllib.parse
from pathlib import Path
import time

def download_jts_pdfs():
    """Download JTS PDFs from known sources"""
    
    # Create PDF directory
    pdf_dir = Path("jts_pdfs")
    pdf_dir.mkdir(exist_ok=True)
    
    # Common JTS PDF sources (you'll need to add actual URLs)
    jts_sources = {
        # Example structure - replace with actual URLs
        "airway_management.pdf": "https://example.com/jts/airway_management.pdf",
        "hemorrhage_control.pdf": "https://example.com/jts/hemorrhage_control.pdf",
        "trauma_assessment.pdf": "https://example.com/jts/trauma_assessment.pdf",
        # Add more as needed
    }
    
    print("JTS PDF Download Helper")
    print("=" * 40)
    print("Note: You'll need to add actual JTS PDF URLs to this script")
    print("or manually copy your PDF files to the jts_pdfs directory.")
    print("\nManual Setup Instructions:")
    print("1. Copy your JTS PDF files to: jts_pdfs/")
    print("2. Run: python jts_processor.py")
    print("3. Start the system: ./run_jts.sh")
    
    return False

def check_pdf_directory():
    """Check what PDFs are in the directory"""
    pdf_dir = Path("jts_pdfs")
    
    if not pdf_dir.exists():
        print("❌ jts_pdfs directory not found")
        return False
    
    pdf_files = list(pdf_dir.glob("*.pdf"))
    
    if not pdf_files:
        print("❌ No PDF files found in jts_pdfs/")
        print("Please add your JTS PDF files to this directory")
        return False
    
    print(f"✅ Found {len(pdf_files)} PDF files:")
    total_size = 0
    
    for pdf_file in pdf_files:
        size_mb = pdf_file.stat().st_size / (1024 * 1024)
        total_size += size_mb
        print(f"   - {pdf_file.name} ({size_mb:.1f}MB)")
    
    print(f"\nTotal size: {total_size:.1f}MB")
    return True

if __name__ == "__main__":
    print("JTS PDF Setup Helper")
    print("=" * 40)
    
    # Check current status
    if check_pdf_directory():
        print("\n✅ PDF files are ready for processing!")
        print("Run: python jts_processor.py")
    else:
        print("\n❌ No PDF files found")
        download_jts_pdfs() 
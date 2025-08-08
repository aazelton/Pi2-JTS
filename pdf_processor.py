#!/usr/bin/env python3
"""
PDF Processor Module
Handles text extraction from PDF files using pdftotext or PyMuPDF
Optimized for Pi2 with minimal memory usage
"""

import os
import sys
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add system Python path for dependencies
sys.path.append('/Users/andrew/Library/Python/3.9/lib/python/site-packages')

logger = logging.getLogger(__name__)

class PDFProcessor:
    def __init__(self, pdf_directory: str = "jts_pdfs", output_directory: str = "processed_data"):
        self.pdf_directory = Path(pdf_directory)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
    def extract_text_pdftotext(self, pdf_path: Path) -> str:
        """Extract text using pdftotext subprocess (light and fast)"""
        try:
            result = subprocess.run(
                ["pdftotext", str(pdf_path), "-"],
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning(f"pdftotext not available, trying PyMuPDF for {pdf_path}")
            return self.extract_text_pymupdf(pdf_path)
    
    def extract_text_pymupdf(self, pdf_path: Path) -> str:
        """Extract text using PyMuPDF (fallback)"""
        try:
            import fitz  # PyMuPDF
            with fitz.open(pdf_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text() + "\n"
                return text
        except ImportError:
            logger.error("No PDF extraction library available")
            return ""
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file using best available method"""
        return self.extract_text_pdftotext(pdf_path)
    
    def process_pdf_directory(self) -> Dict:
        """Process all PDFs in directory and return structured data"""
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        processed_data = {}
        total_size = 0
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            # Extract text
            text = self.extract_text_from_pdf(pdf_file)
            if not text.strip():
                logger.warning(f"No text extracted from {pdf_file.name}")
                continue
            
            # Store processed data
            processed_data[pdf_file.name] = {
                'filename': pdf_file.name,
                'full_text': text,
                'size_bytes': len(text.encode('utf-8')),
                'source_path': str(pdf_file)
            }
            
            total_size += len(text.encode('utf-8'))
        
        # Save processed data
        self.save_processed_data(processed_data, total_size)
        
        return {
            'total_files': len(processed_data),
            'total_size_bytes': total_size,
            'files': list(processed_data.keys())
        }
    
    def save_processed_data(self, data: Dict, total_size: int):
        """Save processed data to JSON files"""
        # Save main data
        output_file = self.output_directory / "extracted_texts.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Save metadata
        metadata = {
            'total_files': len(data),
            'total_size_bytes': total_size,
            'files': list(data.keys())
        }
        
        metadata_file = self.output_directory / "metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved {len(data)} files, {total_size/1024/1024:.1f}MB total")

def main():
    """Test PDF processing"""
    processor = PDFProcessor()
    result = processor.process_pdf_directory()
    print(f"Processed {result['total_files']} files")

if __name__ == "__main__":
    main() 
#!/usr/bin/env python3
"""
JTS (Joint Trauma Services) PDF Processor
Extracts and structures trauma guidelines from PDF documents
Optimized for Pi2 with 128GB storage
"""

import os
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Optional
import logging

# Add system Python packages to path for PyPDF2
sys.path.append('/Users/andrew/Library/Python/3.9/lib/python/site-packages')

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class JTSPDFProcessor:
    def __init__(self, pdf_directory: str = "jts_pdfs", output_directory: str = "jts_data"):
        self.pdf_directory = Path(pdf_directory)
        self.output_directory = Path(output_directory)
        self.output_directory.mkdir(exist_ok=True)
        
        # JTS guideline categories
        self.categories = {
            "airway": ["airway", "intubation", "ventilation", "breathing"],
            "circulation": ["circulation", "hemorrhage", "shock", "blood", "transfusion"],
            "neurological": ["neurological", "brain", "spinal", "GCS", "consciousness"],
            "trauma": ["trauma", "injury", "fracture", "wound", "damage"],
            "emergency": ["emergency", "resuscitation", "critical", "urgent"],
            "surgical": ["surgical", "operation", "procedure", "intervention"],
            "medication": ["medication", "drug", "pharmacology", "treatment"],
            "assessment": ["assessment", "evaluation", "diagnosis", "examination"]
        }
    
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF file"""
        try:
            # Try PyPDF2 first (lighter weight)
            import PyPDF2
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
        except ImportError:
            try:
                # Fallback to pdfplumber
                import pdfplumber
                with pdfplumber.open(pdf_path) as pdf:
                    text = ""
                    for page in pdf.pages:
                        text += page.extract_text() + "\n"
                    return text
            except ImportError:
                logger.error("No PDF extraction library available. Install PyPDF2 or pdfplumber.")
                return ""
    
    def categorize_content(self, text: str, filename: str) -> Dict:
        """Categorize content based on keywords and structure"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Determine primary category
        primary_category = "general"
        max_matches = 0
        
        for category, keywords in self.categories.items():
            matches = sum(1 for keyword in keywords if keyword in text_lower or keyword in filename_lower)
            if matches > max_matches:
                max_matches = matches
                primary_category = category
        
        # Extract key sections
        sections = self.extract_sections(text)
        
        return {
            "filename": filename,
            "category": primary_category,
            "sections": sections,
            "full_text": text,
            "size_bytes": len(text.encode('utf-8'))
        }
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract structured sections from text"""
        sections = {}
        
        # Common JTS section patterns
        section_patterns = [
            r"(?:^|\n)([A-Z][A-Z\s]+:?)\n",
            r"(?:^|\n)(\d+\.\s*[A-Z][^:\n]+:?)\n",
            r"(?:^|\n)([A-Z][a-z\s]+:?)\n"
        ]
        
        lines = text.split('\n')
        current_section = "overview"
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check if this is a section header
            is_header = False
            for pattern in section_patterns:
                if re.match(pattern, line):
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)
                    current_section = line.replace(':', '').strip().lower()
                    current_content = []
                    is_header = True
                    break
            
            if not is_header:
                current_content.append(line)
        
        # Add final section
        if current_content:
            sections[current_section] = '\n'.join(current_content)
        
        return sections
    
    def process_pdf_directory(self) -> Dict:
        """Process all PDFs in the directory"""
        if not self.pdf_directory.exists():
            logger.error(f"PDF directory {self.pdf_directory} does not exist")
            return {}
        
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        processed_data = {}
        total_size = 0
        
        for pdf_file in pdf_files:
            logger.info(f"Processing {pdf_file.name}")
            
            try:
                text = self.extract_text_from_pdf(pdf_file)
                if text:
                    categorized = self.categorize_content(text, pdf_file.name)
                    processed_data[pdf_file.stem] = categorized
                    total_size += categorized['size_bytes']
                    
                    logger.info(f"Processed {pdf_file.name} - Category: {categorized['category']}")
                else:
                    logger.warning(f"No text extracted from {pdf_file.name}")
                    
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
        
        # Save processed data
        self.save_processed_data(processed_data, total_size)
        
        return processed_data
    
    def save_processed_data(self, data: Dict, total_size: int):
        """Save processed data to JSON files"""
        # Save by category for efficient access
        categorized_data = {}
        
        for filename, content in data.items():
            category = content['category']
            if category not in categorized_data:
                categorized_data[category] = {}
            categorized_data[category][filename] = content
        
        # Save each category separately
        for category, category_data in categorized_data.items():
            output_file = self.output_directory / f"{category}_guidelines.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(category_data, f, indent=2, ensure_ascii=False)
        
        # Save metadata
        metadata = {
            "total_files": len(data),
            "total_size_bytes": total_size,
            "categories": list(categorized_data.keys()),
            "files_by_category": {cat: len(files) for cat, files in categorized_data.items()}
        }
        
        with open(self.output_directory / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved {len(data)} files, {total_size/1024/1024:.1f}MB total")
        logger.info(f"Categories: {list(categorized_data.keys())}")

def main():
    """Main processing function"""
    processor = JTSPDFProcessor()
    processor.process_pdf_directory()

if __name__ == "__main__":
    main() 
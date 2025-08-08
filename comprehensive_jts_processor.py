#!/usr/bin/env python3
"""
Comprehensive JTS Processor for P2 Clinical Assist
Extracts ALL JTS protocols from the complete library (~100 PDFs)
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import logging
import fitz  # PyMuPDF

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ComprehensiveJTSProcessor:
    def __init__(self, pdf_directory: str = "../jts_pdfs"):
        self.pdf_directory = Path(pdf_directory)
        self.comprehensive_corpus = []
        self.protocol_categories = {
            'airway': ['airway', 'intubation', 'ventilation', 'respiratory'],
            'cardiac': ['cardiac', 'heart', 'ecg', 'defibrillation', 'cpr'],
            'trauma': ['trauma', 'injury', 'fracture', 'amputation', 'crush'],
            'hemorrhage': ['bleeding', 'hemorrhage', 'blood', 'transfusion', 'shock'],
            'neurological': ['brain', 'tbi', 'neurological', 'spine', 'concussion'],
            'burn': ['burn', 'thermal', 'inhalation'],
            'pediatric': ['pediatric', 'child', 'infant'],
            'obstetric': ['obstetric', 'pregnancy', 'delivery', 'uterine'],
            'medication': ['medication', 'drug', 'analgesia', 'sedation'],
            'surgical': ['surgical', 'operation', 'procedure'],
            'emergency': ['emergency', 'urgent', 'critical'],
            'monitoring': ['monitoring', 'assessment', 'vital', 'signs'],
            'transport': ['transport', 'evacuation', 'en route'],
            'cbrn': ['chemical', 'biological', 'radiological', 'nuclear', 'cbrn'],
            'environmental': ['heat', 'cold', 'altitude', 'drowning'],
            'infection': ['infection', 'sepsis', 'antibiotic', 'wound'],
            'mwd': ['mwd', 'k9', 'canine', 'dog']
        }
        
    def extract_text_from_pdf(self, pdf_path: Path) -> str:
        """Extract text from PDF using PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            return text
        except Exception as e:
            logger.warning(f"Failed to extract text from {pdf_path}: {e}")
            return ""
    
    def categorize_protocol(self, filename: str, text: str) -> List[str]:
        """Categorize protocol based on filename and content"""
        categories = []
        filename_lower = filename.lower()
        text_lower = text.lower()
        
        for category, keywords in self.protocol_categories.items():
            # Check filename
            if any(keyword in filename_lower for keyword in keywords):
                categories.append(category)
            # Check content
            elif any(keyword in text_lower for keyword in keywords):
                categories.append(category)
        
        return list(set(categories)) if categories else ['general']
    
    def extract_clinical_sections(self, text: str, filename: str) -> List[Dict[str, Any]]:
        """Extract clinical sections from protocol text"""
        sections = []
        
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        
        for i, paragraph in enumerate(paragraphs):
            paragraph = paragraph.strip()
            if len(paragraph) < 50:  # Skip very short paragraphs
                continue
                
            # Check if paragraph contains clinical content
            if self._is_clinical_content(paragraph):
                # Extract clinical information
                clinical_info = self._extract_clinical_info(paragraph)
                
                sections.append({
                    'text': paragraph,
                    'section': f"Section_{i+1}",
                    'source': filename,
                    'categories': self.categorize_protocol(filename, paragraph),
                    'clinical_info': clinical_info,
                    'priority_score': self._calculate_priority_score(paragraph, clinical_info),
                    'protocol_type': 'comprehensive_jts'
                })
        
        return sections
    
    def _is_clinical_content(self, text: str) -> bool:
        """Determine if text contains clinical content"""
        if not text or len(text.strip()) < 50:
            return False
            
        clinical_keywords = [
            'treatment', 'medication', 'dose', 'mg', 'mcg', 'ml', 'iv', 'im', 'po',
            'protocol', 'guideline', 'procedure', 'assessment', 'monitor',
            'airway', 'breathing', 'circulation', 'hemorrhage', 'shock',
            'trauma', 'cardiac', 'respiratory', 'neurological', 'pediatric',
            'adult', 'emergency', 'critical', 'resuscitation', 'ventilation',
            'intubation', 'defibrillation', 'cpr', 'bradycardia', 'tachycardia',
            'hypertension', 'hypotension', 'hypoxia', 'hypercapnia', 'administer',
            'give', 'apply', 'insert', 'perform', 'check', 'assess', 'evaluate'
        ]
        
        text_lower = text.lower()
        keyword_count = sum(1 for keyword in clinical_keywords if keyword in text_lower)
        
        # Must have at least 2 clinical keywords
        return keyword_count >= 2
    
    def _extract_clinical_info(self, text: str) -> Dict[str, Any]:
        """Extract structured clinical information from text"""
        clinical_info = {
            'medications': [],
            'dosages': [],
            'procedures': [],
            'indications': [],
            'contraindications': [],
            'monitoring': [],
            'complications': []
        }
        
        # Extract medications and dosages
        medication_patterns = [
            r'(\w+)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|units?)\s*(iv|im|po|sc|io)?',
            r'(\w+)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|units?)/(kg|min|hr|day)',
            r'(\w+)\s+(\d+(?:\.\d+)?)\s*(mg|mcg|ml|g|units?)\s*(every|q|per)\s*(\d+)\s*(min|hr|day)'
        ]
        
        for pattern in medication_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                medication = match.group(1).lower()
                dosage = match.group(2)
                unit = match.group(3)
                route = match.group(4) if len(match.groups()) > 3 else ''
                
                clinical_info['medications'].append({
                    'name': medication,
                    'dosage': f"{dosage} {unit}",
                    'route': route,
                    'full_match': match.group(0)
                })
        
        # Extract procedures
        procedure_keywords = [
            'intubation', 'defibrillation', 'cpr', 'chest compression', 'ventilation',
            'needle decompression', 'chest tube', 'tourniquet', 'packing', 'splinting',
            'intraosseous', 'central line', 'arterial line', 'cricothyrotomy',
            'thoracotomy', 'laparotomy', 'amputation', 'debridement', 'irrigation'
        ]
        
        for keyword in procedure_keywords:
            if keyword.lower() in text.lower():
                clinical_info['procedures'].append(keyword)
        
        # Extract indications and contraindications
        indication_patterns = [
            r'indication[s]?\s*[:•]\s*(.+)',
            r'when\s+to\s+(use|administer|perform)\s*[:•]\s*(.+)',
            r'for\s+(.+?)(?:\.|$)'
        ]
        
        contraindication_patterns = [
            r'contraindication[s]?\s*[:•]\s*(.+)',
            r'do\s+not\s+(use|administer|perform)\s*[:•]\s*(.+)',
            r'avoid\s+(.+?)(?:\.|$)'
        ]
        
        for pattern in indication_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                clinical_info['indications'].append(match.group(1).strip())
        
        for pattern in contraindication_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                clinical_info['contraindications'].append(match.group(1).strip())
        
        return clinical_info
    
    def _calculate_priority_score(self, text: str, clinical_info: Dict[str, Any]) -> float:
        """Calculate priority score for protocol relevance"""
        score = 0.0
        
        # Base score for clinical content
        if self._is_clinical_content(text):
            score += 10.0
        
        # Bonus for medications
        score += len(clinical_info['medications']) * 2.0
        
        # Bonus for procedures
        score += len(clinical_info['procedures']) * 1.5
        
        # Bonus for specific clinical scenarios
        emergency_keywords = ['cardiac arrest', 'hemorrhage', 'airway', 'shock', 'trauma', 'emergency']
        for keyword in emergency_keywords:
            if keyword.lower() in text.lower():
                score += 5.0
        
        # Bonus for dosage information
        if clinical_info['dosages']:
            score += 3.0
        
        # Penalty for very long text (less focused)
        if len(text) > 2000:
            score -= 2.0
        
        return score
    
    def process_all_jts_protocols(self) -> List[Dict[str, Any]]:
        """Process ALL JTS protocols in the directory"""
        logger.info(f"Processing JTS protocols from {self.pdf_directory}")
        
        if not self.pdf_directory.exists():
            logger.error(f"PDF directory not found: {self.pdf_directory}")
            return []
        
        # Get all PDF files
        pdf_files = list(self.pdf_directory.glob("*.pdf"))
        logger.info(f"Found {len(pdf_files)} PDF files")
        
        total_sections = 0
        
        for pdf_file in pdf_files:
            try:
                logger.info(f"Processing {pdf_file.name}")
                
                # Extract text
                text = self.extract_text_from_pdf(pdf_file)
                if not text:
                    continue
                
                # Extract clinical sections
                sections = self.extract_clinical_sections(text, pdf_file.name)
                self.comprehensive_corpus.extend(sections)
                
                total_sections += len(sections)
                logger.info(f"Extracted {len(sections)} clinical sections from {pdf_file.name}")
                
            except Exception as e:
                logger.error(f"Error processing {pdf_file.name}: {e}")
                continue
        
        # Sort by priority score
        self.comprehensive_corpus.sort(key=lambda x: x.get('priority_score', 0), reverse=True)
        
        logger.info(f"Total clinical sections extracted: {total_sections}")
        return self.comprehensive_corpus
    
    def save_comprehensive_corpus(self, output_path: str = "jts_comprehensive_corpus.json") -> None:
        """Save comprehensive corpus to file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(self.comprehensive_corpus, f, indent=2, ensure_ascii=False)
            logger.info(f"Saved comprehensive corpus to {output_path}")
        except Exception as e:
            logger.error(f"Failed to save comprehensive corpus: {e}")
    
    def get_corpus_statistics(self) -> Dict[str, Any]:
        """Get statistics about the comprehensive corpus"""
        stats = {
            'total_entries': len(self.comprehensive_corpus),
            'categories': {},
            'protocol_types': {},
            'avg_priority_score': 0.0,
            'medication_count': 0,
            'procedure_count': 0
        }
        
        if not self.comprehensive_corpus:
            return stats
        
        # Count categories
        for entry in self.comprehensive_corpus:
            categories = entry.get('categories', [])
            for category in categories:
                stats['categories'][category] = stats['categories'].get(category, 0) + 1
        
        # Count protocol types
        for entry in self.comprehensive_corpus:
            protocol_type = entry.get('protocol_type', 'unknown')
            stats['protocol_types'][protocol_type] = stats['protocol_types'].get(protocol_type, 0) + 1
        
        # Calculate average priority score
        priority_scores = [entry.get('priority_score', 0) for entry in self.comprehensive_corpus]
        stats['avg_priority_score'] = sum(priority_scores) / len(priority_scores)
        
        # Count medications and procedures
        for entry in self.comprehensive_corpus:
            clinical_info = entry.get('clinical_info', {})
            stats['medication_count'] += len(clinical_info.get('medications', []))
            stats['procedure_count'] += len(clinical_info.get('procedures', []))
        
        return stats

def main():
    """Main processing function"""
    processor = ComprehensiveJTSProcessor()
    
    # Process all JTS protocols
    comprehensive_corpus = processor.process_all_jts_protocols()
    
    # Save comprehensive corpus
    processor.save_comprehensive_corpus()
    
    # Get and display statistics
    stats = processor.get_corpus_statistics()
    
    logger.info("=== COMPREHENSIVE JTS CORPUS STATISTICS ===")
    logger.info(f"Total entries: {stats['total_entries']}")
    logger.info(f"Average priority score: {stats['avg_priority_score']:.2f}")
    logger.info(f"Total medications found: {stats['medication_count']}")
    logger.info(f"Total procedures found: {stats['procedure_count']}")
    
    logger.info("\nCategories:")
    for category, count in sorted(stats['categories'].items(), key=lambda x: x[1], reverse=True):
        logger.info(f"  {category}: {count}")
    
    logger.info("\nProtocol types:")
    for protocol_type, count in stats['protocol_types'].items():
        logger.info(f"  {protocol_type}: {count}")

if __name__ == "__main__":
    main() 
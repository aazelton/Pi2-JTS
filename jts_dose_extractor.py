#!/usr/bin/env python3
"""
JTS Dose Extractor
Uses BM25 to find specific medication dosing information
"""

import json
from rank_bm25 import BM25Okapi
import re

class JTSDoseExtractor:
    def __init__(self, corpus_file="jts_corpus.json"):
        """Initialize with JTS corpus file"""
        self.corpus_file = corpus_file
        self.paragraphs = []
        self.bm25 = None
        self.load_corpus()
        self.build_index()
    
    def load_corpus(self):
        """Load paragraphs from JSON corpus file"""
        print(f"📚 Loading JTS corpus from {self.corpus_file}...")
        try:
            with open(self.corpus_file, 'r', encoding='utf-8') as f:
                self.paragraphs = json.load(f)
            print(f"✅ Loaded {len(self.paragraphs)} paragraphs")
        except Exception as e:
            print(f"❌ Error loading corpus: {e}")
            self.paragraphs = []
    
    def build_index(self):
        """Build BM25 index from paragraphs"""
        if not self.paragraphs:
            print("❌ No paragraphs to index")
            return
        
        print("🔍 Building BM25 index...")
        
        # Tokenize paragraphs
        tokenized = []
        for p in self.paragraphs:
            # Clean and tokenize text
            text = p["text"].lower()
            # Remove extra whitespace and split
            tokens = re.sub(r'\s+', ' ', text).strip().split()
            tokenized.append(tokens)
        
        # Build BM25 index
        self.bm25 = BM25Okapi(tokenized)
        print("✅ BM25 index built successfully")
    
    def extract_ketamine_dose(self, weight_kg=None):
        """Extract ketamine dosing information"""
        query = "ketamine dose mg/kg"
        results = self.bm25.get_top_n(query.split(), self.paragraphs, n=5)
        
        print(f"🔍 Ketamine dosing information:")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            text = result['text']
            source = result['source']
            page = result['page']
            
            # Look for dosing patterns
            dose_patterns = [
                r'(\d+(?:\.\d+)?)\s*mg/kg',
                r'ketamine.*?(\d+(?:\.\d+)?)\s*mg',
                r'(\d+(?:\.\d+)?)\s*mg.*?ketamine'
            ]
            
            for pattern in dose_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"\n📋 Result {i} (Source: {source}, Page: {page}):")
                    print(f"   Dose found: {matches[0]} mg/kg")
                    
                    if weight_kg:
                        try:
                            dose_mg = float(matches[0]) * weight_kg
                            print(f"   For {weight_kg} kg patient: {dose_mg:.1f} mg")
                        except ValueError:
                            pass
                    
                    # Extract the relevant sentence
                    sentences = text.split('.')
                    for sentence in sentences:
                        if 'ketamine' in sentence.lower() and any(match in sentence for match in matches):
                            print(f"   Context: {sentence.strip()}")
                            break
                    break
        
        return results
    
    def extract_txa_dose(self):
        """Extract TXA dosing information"""
        query = "tranexamic acid TXA dose"
        results = self.bm25.get_top_n(query.split(), self.paragraphs, n=5)
        
        print(f"\n🔍 TXA dosing information:")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            text = result['text']
            source = result['source']
            page = result['page']
            
            # Look for TXA dosing patterns
            dose_patterns = [
                r'(\d+)\s*(?:mg|g).*?tranexamic',
                r'tranexamic.*?(\d+)\s*(?:mg|g)',
                r'(\d+)\s*(?:mg|g).*?TXA'
            ]
            
            for pattern in dose_patterns:
                matches = re.findall(pattern, text, re.IGNORECASE)
                if matches:
                    print(f"\n📋 Result {i} (Source: {source}, Page: {page}):")
                    print(f"   Dose found: {matches[0]} mg")
                    
                    # Extract the relevant sentence
                    sentences = text.split('.')
                    for sentence in sentences:
                        if ('tranexamic' in sentence.lower() or 'txa' in sentence.lower()) and matches[0] in sentence:
                            print(f"   Context: {sentence.strip()}")
                            break
                    break
        
        return results
    
    def extract_procedure(self, procedure_name):
        """Extract procedure information"""
        query = f"{procedure_name} procedure"
        results = self.bm25.get_top_n(query.split(), self.paragraphs, n=3)
        
        print(f"\n🔍 {procedure_name.title()} procedure information:")
        print("=" * 50)
        
        for i, result in enumerate(results, 1):
            text = result['text']
            source = result['source']
            page = result['page']
            
            print(f"\n📋 Result {i} (Source: {source}, Page: {page}):")
            
            # Extract actionable steps
            action_verbs = ['apply', 'insert', 'perform', 'administer', 'monitor', 'check']
            sentences = text.split('.')
            
            for sentence in sentences:
                if any(verb in sentence.lower() for verb in action_verbs):
                    if len(sentence.strip()) > 20:  # Avoid very short sentences
                        print(f"   Step: {sentence.strip()}")
            
            # Show first 200 chars if no specific steps found
            if len(text) > 200:
                print(f"   Text: {text[:200]}...")
            else:
                print(f"   Text: {text}")
        
        return results

def main():
    """Main function to test the dose extractor"""
    print("🎯 JTS Dose Extractor")
    print("=" * 40)
    
    # Initialize system
    extractor = JTSDoseExtractor()
    
    # Extract ketamine dosing for 80kg patient
    extractor.extract_ketamine_dose(weight_kg=80)
    
    # Extract TXA dosing
    extractor.extract_txa_dose()
    
    # Extract tourniquet procedure
    extractor.extract_procedure("tourniquet")
    
    # Extract airway management
    extractor.extract_procedure("airway")

if __name__ == "__main__":
    main() 
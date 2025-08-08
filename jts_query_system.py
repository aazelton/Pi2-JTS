#!/usr/bin/env python3
"""
Interactive JTS Query System
Allows users to ask questions and get specific dosing information
"""

import json
from rank_bm25 import BM25Okapi
import re

class JTSQuerySystem:
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
    
    def query(self, query_text, n=3):
        """Perform BM25 query and return top n results"""
        if not self.bm25:
            print("❌ BM25 index not built")
            return []
        
        # Tokenize query
        query_tokens = query_text.lower().split()
        
        # Get top n results
        results = self.bm25.get_top_n(query_tokens, self.paragraphs, n=n)
        
        return results
    
    def extract_dose(self, query_text, weight_kg=None):
        """Extract specific dosing information from query"""
        results = self.query(query_text, n=5)
        
        print(f"\n🔍 Query: {query_text}")
        print("=" * 50)
        
        # Look for medication names
        medications = {
            'ketamine': r'(\d+(?:\.\d+)?)\s*mg/kg.*?ketamine|ketamine.*?(\d+(?:\.\d+)?)\s*mg/kg',
            'morphine': r'(\d+(?:\.\d+)?)\s*mg.*?morphine|morphine.*?(\d+(?:\.\d+)?)\s*mg',
            'fentanyl': r'(\d+(?:\.\d+)?)\s*mcg.*?fentanyl|fentanyl.*?(\d+(?:\.\d+)?)\s*mcg',
            'txa': r'(\d+)\s*(?:mg|g).*?tranexamic|tranexamic.*?(\d+)\s*(?:mg|g)',
            'epinephrine': r'(\d+(?:\.\d+)?)\s*mg.*?epinephrine|epinephrine.*?(\d+(?:\.\d+)?)\s*mg'
        }
        
        found_doses = []
        
        for i, result in enumerate(results, 1):
            text = result['text']
            source = result['source']
            page = result['page']
            
            # Check for medication dosing
            for med_name, pattern in medications.items():
                if med_name in query_text.lower():
                    matches = re.findall(pattern, text, re.IGNORECASE)
                    if matches:
                        # Flatten matches and get first non-empty value
                        for match in matches:
                            if isinstance(match, tuple):
                                dose = next((m for m in match if m), None)
                            else:
                                dose = match
                            
                            if dose:
                                found_doses.append({
                                    'medication': med_name,
                                    'dose': dose,
                                    'source': source,
                                    'page': page,
                                    'context': text[:200] + "..." if len(text) > 200 else text
                                })
                                
                                print(f"\n📋 {med_name.title()} dosing found:")
                                print(f"   Dose: {dose}")
                                
                                if weight_kg and 'mg/kg' in pattern:
                                    try:
                                        total_dose = float(dose) * weight_kg
                                        print(f"   For {weight_kg} kg patient: {total_dose:.1f} mg")
                                    except ValueError:
                                        pass
                                
                                print(f"   Source: {source} (Page {page})")
                                break
        
        if not found_doses:
            print("❌ No specific dosing information found")
            print("\n📋 Top results:")
            for i, result in enumerate(results, 1):
                print(f"\nResult {i}:")
                print(f"Source: {result['source']} (Page {result['page']})")
                print(f"Text: {result['text'][:200]}...")
        
        return found_doses
    
    def interactive_query(self):
        """Interactive query loop"""
        print("\n🎯 JTS Interactive Query System")
        print("=" * 40)
        print("Ask questions like:")
        print("- 'ketamine dose for 80 kg patient'")
        print("- 'TXA dosing'")
        print("- 'tourniquet application'")
        print("- 'airway management'")
        print("- Type 'quit' to exit")
        print("=" * 40)
        
        while True:
            try:
                query = input("\n🔍 Enter your query: ").strip()
                
                if query.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                
                if not query:
                    continue
                
                # Extract weight if mentioned
                weight_match = re.search(r'(\d+)\s*kg', query)
                weight_kg = int(weight_match.group(1)) if weight_match else None
                
                # Check if it's a dosing query
                if any(med in query.lower() for med in ['ketamine', 'morphine', 'fentanyl', 'txa', 'tranexamic', 'epinephrine']):
                    self.extract_dose(query, weight_kg)
                else:
                    # General query
                    results = self.query(query, n=3)
                    print(f"\n🔍 Query: {query}")
                    print("=" * 50)
                    
                    for i, result in enumerate(results, 1):
                        print(f"\n📋 Result {i}:")
                        print(f"Source: {result['source']} (Page {result['page']})")
                        print(f"Text: {result['text'][:300]}...")
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

def main():
    """Main function"""
    system = JTSQuerySystem()
    system.interactive_query()

if __name__ == "__main__":
    main() 
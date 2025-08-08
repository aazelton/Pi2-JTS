#!/usr/bin/env python3
"""
Test BM25 Queries for JTS Corpus
Demonstrates the BM25 query system with predefined queries
"""

import json
from rank_bm25 import BM25Okapi
import re

def load_corpus(corpus_file="jts_corpus.json"):
    """Load paragraphs from JSON corpus file"""
    print(f"📚 Loading JTS corpus from {corpus_file}...")
    try:
        with open(corpus_file, 'r', encoding='utf-8') as f:
            paragraphs = json.load(f)
        print(f"✅ Loaded {len(paragraphs)} paragraphs")
        return paragraphs
    except Exception as e:
        print(f"❌ Error loading corpus: {e}")
        return []

def build_bm25_index(paragraphs):
    """Build BM25 index from paragraphs"""
    if not paragraphs:
        print("❌ No paragraphs to index")
        return None
    
    print("🔍 Building BM25 index...")
    
    # Tokenize paragraphs
    tokenized = []
    for p in paragraphs:
        # Clean and tokenize text
        text = p["text"].lower()
        # Remove extra whitespace and split
        tokens = re.sub(r'\s+', ' ', text).strip().split()
        tokenized.append(tokens)
    
    # Build BM25 index
    bm25 = BM25Okapi(tokenized)
    print("✅ BM25 index built successfully")
    return bm25

def query_bm25(bm25, paragraphs, query_text, n=3):
    """Perform BM25 query and return top n results"""
    if not bm25:
        print("❌ BM25 index not built")
        return []
    
    # Tokenize query
    query_tokens = query_text.lower().split()
    
    # Get top n results
    results = bm25.get_top_n(query_tokens, paragraphs, n=n)
    
    return results

def extract_ketamine_dose(paragraphs, bm25, weight_kg=None):
    """Extract ketamine dosing information"""
    query = "ketamine dose mg/kg"
    results = query_bm25(bm25, paragraphs, query, n=5)
    
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

def main():
    """Main function to test BM25 queries"""
    print("🎯 JTS BM25 Query Test")
    print("=" * 40)
    
    # Load corpus
    paragraphs = load_corpus()
    if not paragraphs:
        return
    
    # Build BM25 index
    bm25 = build_bm25_index(paragraphs)
    if not bm25:
        return
    
    # Test queries
    test_queries = [
        "ketamine dose for 80 kg",
        "TXA tranexamic acid",
        "tourniquet application",
        "airway management"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        results = query_bm25(bm25, paragraphs, query, n=2)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {result['source']}")
            print(f"Page: {result['page']}")
            print(f"Text: {result['text'][:200]}...")
    
    # Specific ketamine dose extraction
    print(f"\n🎯 Specific ketamine dose extraction:")
    extract_ketamine_dose(paragraphs, bm25, weight_kg=80)

if __name__ == "__main__":
    main() 
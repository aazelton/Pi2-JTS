#!/usr/bin/env python3
"""
Simple BM25 JTS Query System
Loads jts_corpus.json and performs BM25 queries
"""

import json
from rank_bm25 import BM25Okapi
import re

class JTSBM25Query:
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
    
    def search_ketamine(self, weight=None):
        """Search for ketamine dosing information"""
        query = "ketamine dose"
        if weight:
            query += f" {weight} kg"
        
        print(f"🔍 Searching for: {query}")
        results = self.query(query, n=3)
        
        print(f"\n📋 Top {len(results)} results:")
        for i, result in enumerate(results, 1):
            print(f"\n--- Result {i} ---")
            print(f"Source: {result['source']}")
            print(f"Page: {result['page']}")
            print(f"Text: {result['text'][:300]}...")
        
        return results

def main():
    """Main function to test the BM25 system"""
    print("🎯 JTS BM25 Query System")
    print("=" * 40)
    
    # Initialize system
    jts_query = JTSBM25Query()
    
    # Test queries
    test_queries = [
        "ketamine dose for 80 kg",
        "TXA tranexamic acid",
        "tourniquet application",
        "airway management",
        "pain management"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 30)
        results = jts_query.query(query, n=2)
        
        for i, result in enumerate(results, 1):
            print(f"\nResult {i}:")
            print(f"Source: {result['source']}")
            print(f"Page: {result['page']}")
            print(f"Text: {result['text'][:200]}...")
    
    # Specific ketamine search
    print(f"\n🎯 Specific ketamine search:")
    jts_query.search_ketamine(weight=80)

if __name__ == "__main__":
    main() 
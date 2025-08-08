#!/usr/bin/env python3
"""
Text Indexer Module
Handles text indexing using TF-IDF or BM25 for efficient query matching
Optimized for Pi2 with minimal memory usage
"""

import json
import pickle
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

# Add system Python path for dependencies
sys.path.append('/Users/andrew/Library/Python/3.9/lib/python/site-packages')

logger = logging.getLogger(__name__)

class TextIndexer:
    def __init__(self, data_directory: str = "processed_data", index_directory: str = "text_index"):
        self.data_directory = Path(data_directory)
        self.index_directory = Path(index_directory)
        self.index_directory.mkdir(exist_ok=True)
        
        self.index = None
        self.documents = []
        self.document_ids = []
        
    def load_processed_data(self) -> Dict:
        """Load processed PDF data"""
        data_file = self.data_directory / "extracted_texts.json"
        if not data_file.exists():
            raise FileNotFoundError(f"Processed data not found at {data_file}")
        
        with open(data_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_tfidf_index(self, documents: List[str]) -> object:
        """Create TF-IDF index using scikit-learn"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.metrics.pairwise import cosine_similarity
            
            # Create TF-IDF vectorizer with minimal memory usage
            vectorizer = TfidfVectorizer(
                max_features=10000,  # Limit features for memory efficiency
                stop_words='english',
                ngram_range=(1, 2),  # Unigrams and bigrams
                min_df=2,  # Minimum document frequency
                max_df=0.95  # Maximum document frequency
            )
            
            # Fit and transform documents
            tfidf_matrix = vectorizer.fit_transform(documents)
            
            return {
                'vectorizer': vectorizer,
                'matrix': tfidf_matrix,
                'type': 'tfidf'
            }
            
        except ImportError:
            logger.warning("scikit-learn not available, using simple text matching")
            return self.create_simple_index(documents)
    
    def create_bm25_index(self, documents: List[str]) -> object:
        """Create BM25 index using rank_bm25"""
        try:
            from rank_bm25 import BM25Okapi
            import re
            
            # Tokenize documents
            tokenized_docs = []
            for doc in documents:
                tokens = re.findall(r'\w+', doc.lower())
                tokenized_docs.append(tokens)
            
            # Create BM25 index
            bm25 = BM25Okapi(tokenized_docs)
            
            return {
                'bm25': bm25,
                'documents': tokenized_docs,
                'type': 'bm25'
            }
            
        except ImportError:
            logger.warning("rank_bm25 not available, using simple text matching")
            return self.create_simple_index(documents)
    
    def create_simple_index(self, documents: List[str]) -> object:
        """Create simple keyword-based index as fallback"""
        index = {}
        
        for i, doc in enumerate(documents):
            words = doc.lower().split()
            for word in words:
                if len(word) > 3:  # Only index words longer than 3 characters
                    if word not in index:
                        index[word] = []
                    if i not in index[word]:
                        index[word].append(i)
        
        return {
            'index': index,
            'documents': documents,
            'type': 'simple'
        }
    
    def build_index(self, index_type: str = "tfidf") -> Dict:
        """Build text index from processed data"""
        logger.info("Loading processed data...")
        data = self.load_processed_data()
        
        # Prepare documents
        self.documents = []
        self.document_ids = []
        
        for filename, content in data.items():
            self.documents.append(content['full_text'])
            self.document_ids.append(filename)
        
        logger.info(f"Indexing {len(self.documents)} documents...")
        
        # Create index based on type
        if index_type == "tfidf":
            self.index = self.create_tfidf_index(self.documents)
        elif index_type == "bm25":
            self.index = self.create_bm25_index(self.documents)
        else:
            self.index = self.create_simple_index(self.documents)
        
        # Save index
        self.save_index()
        
        return {
            'index_type': self.index['type'],
            'document_count': len(self.documents),
            'index_size': len(self.documents)
        }
    
    def search_tfidf(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search using TF-IDF"""
        from sklearn.metrics.pairwise import cosine_similarity
        
        # Transform query
        query_vector = self.index['vectorizer'].transform([query])
        
        # Calculate similarities
        similarities = cosine_similarity(query_vector, self.index['matrix']).flatten()
        
        # Get top results
        top_indices = similarities.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if similarities[idx] > 0:  # Only return relevant results
                results.append((idx, float(similarities[idx])))
        
        return results
    
    def search_bm25(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search using BM25"""
        import re
        
        # Tokenize query
        query_tokens = re.findall(r'\w+', query.lower())
        
        # Get scores
        scores = self.index['bm25'].get_scores(query_tokens)
        
        # Get top results
        top_indices = scores.argsort()[-top_k:][::-1]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only return relevant results
                results.append((idx, float(scores[idx])))
        
        return results
    
    def search_simple(self, query: str, top_k: int = 5) -> List[Tuple[int, float]]:
        """Search using simple keyword matching"""
        query_words = query.lower().split()
        scores = [0] * len(self.documents)
        
        for i, doc in enumerate(self.documents):
            doc_lower = doc.lower()
            for word in query_words:
                if len(word) > 3 and word in doc_lower:
                    scores[i] += 1
        
        # Get top results
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        
        results = []
        for idx in top_indices:
            if scores[idx] > 0:  # Only return relevant results
                results.append((idx, float(scores[idx])))
        
        return results
    
    def search(self, query: str, top_k: int = 5) -> List[Dict]:
        """Search documents and return results"""
        if not self.index:
            raise ValueError("Index not built. Call build_index() first.")
        
        # Search based on index type
        if self.index['type'] == 'tfidf':
            results = self.search_tfidf(query, top_k)
        elif self.index['type'] == 'bm25':
            results = self.search_bm25(query, top_k)
        else:
            results = self.search_simple(query, top_k)
        
        # Format results
        formatted_results = []
        for idx, score in results:
            formatted_results.append({
                'document_id': self.document_ids[idx],
                'content': self.documents[idx][:500] + "..." if len(self.documents[idx]) > 500 else self.documents[idx],
                'score': score,
                'index': idx
            })
        
        return formatted_results
    
    def save_index(self):
        """Save index to disk"""
        index_file = self.index_directory / "text_index.pkl"
        with open(index_file, 'wb') as f:
            pickle.dump({
                'index': self.index,
                'documents': self.documents,
                'document_ids': self.document_ids
            }, f)
        
        logger.info(f"Index saved to {index_file}")
    
    def load_index(self):
        """Load index from disk"""
        index_file = self.index_directory / "text_index.pkl"
        if not index_file.exists():
            raise FileNotFoundError(f"Index not found at {index_file}")
        
        with open(index_file, 'rb') as f:
            data = pickle.load(f)
            self.index = data['index']
            self.documents = data['documents']
            self.document_ids = data['document_ids']
        
        logger.info(f"Index loaded from {index_file}")

def main():
    """Test text indexing"""
    indexer = TextIndexer()
    
    # Build index
    result = indexer.build_index("tfidf")
    print(f"Built {result['index_type']} index with {result['document_count']} documents")
    
    # Test search
    query = "ketamine dosage"
    results = indexer.search(query, top_k=3)
    
    print(f"\nSearch results for '{query}':")
    for i, result in enumerate(results):
        print(f"{i+1}. {result['document_id']} (score: {result['score']:.3f})")

if __name__ == "__main__":
    main() 
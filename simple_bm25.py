#!/usr/bin/env python3
"""
Simple BM25 Implementation
Lightweight BM25 search algorithm for JTS Recall Engine
No external dependencies required
"""

import math
import re
from typing import List, Dict
from collections import Counter

class SimpleBM25:
    """Simple BM25 implementation for document search"""
    
    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 with documents
        
        Args:
            documents: List of document texts
            k1: BM25 parameter (default 1.5)
            b: BM25 parameter (default 0.75)
        """
        self.documents = documents
        self.k1 = k1
        self.b = b
        
        # Tokenize documents
        self.tokenized_docs = [self._tokenize(doc) for doc in documents]
        
        # Calculate document frequencies
        self.doc_freq = self._calculate_doc_freq()
        
        # Calculate average document length
        self.avg_doc_len = sum(len(doc) for doc in self.tokenized_docs) / len(self.tokenized_docs)
        
    def _tokenize(self, text: str) -> List[str]:
        """Improved tokenization - split on whitespace, lowercase, and filter"""
        # Convert to lowercase and split
        tokens = text.lower().split()
        
        # Filter out very short tokens and common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'me', 'him', 'her', 'us', 'them'}
        
        # Keep only meaningful tokens
        filtered_tokens = []
        for token in tokens:
            # Remove punctuation and clean token
            clean_token = re.sub(r'[^\w\s]', '', token)
            if len(clean_token) > 2 and clean_token not in stop_words:
                filtered_tokens.append(clean_token)
        
        return filtered_tokens
    
    def _calculate_doc_freq(self) -> Dict[str, int]:
        """Calculate document frequency for each term"""
        doc_freq = Counter()
        for doc in self.tokenized_docs:
            unique_terms = set(doc)
            for term in unique_terms:
                doc_freq[term] += 1
        return doc_freq
    
    def _calculate_idf(self, term: str) -> float:
        """Calculate inverse document frequency for a term"""
        if term not in self.doc_freq:
            return 0
        
        N = len(self.documents)
        df = self.doc_freq[term]
        
        if df == 0:
            return 0
        
        return math.log((N - df + 0.5) / (df + 0.5))
    
    def _calculate_bm25_score(self, doc_tokens: List[str], query_tokens: List[str]) -> float:
        """Calculate BM25 score for a document given query"""
        score = 0.0
        
        for term in query_tokens:
            if term not in self.doc_freq:
                continue
                
            idf = self._calculate_idf(term)
            term_freq = doc_tokens.count(term)
            doc_len = len(doc_tokens)
            
            # BM25 formula
            numerator = term_freq * (self.k1 + 1)
            denominator = term_freq + self.k1 * (1 - self.b + self.b * (doc_len / self.avg_doc_len))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def search(self, query: str, top_n: int = 3) -> List[int]:
        """
        Search documents and return top N document indices
        
        Args:
            query: Search query
            top_n: Number of top results to return
            
        Returns:
            List of document indices sorted by relevance
        """
        query_tokens = self._tokenize(query)
        
        # If no meaningful tokens, return empty
        if not query_tokens:
            return []
        
        # Calculate scores for all documents
        scores = []
        for i, doc_tokens in enumerate(self.tokenized_docs):
            score = self._calculate_bm25_score(doc_tokens, query_tokens)
            scores.append((score, i))
        
        # Sort by score (descending) and return top N
        scores.sort(reverse=True)
        return [doc_idx for score, doc_idx in scores[:top_n] if score > 0]

def create_bm25_index(corpus: List[Dict]) -> SimpleBM25:
    """
    Create BM25 index from corpus
    
    Args:
        corpus: List of corpus entries with 'text' field
        
    Returns:
        SimpleBM25 index
    """
    documents = [entry['text'] for entry in corpus]
    return SimpleBM25(documents) 
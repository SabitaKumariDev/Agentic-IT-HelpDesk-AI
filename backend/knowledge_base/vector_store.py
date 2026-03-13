"""
Vector Store - Hybrid Search Engine
Combines TF-IDF cosine similarity with BM25 scoring for robust retrieval.
Includes retrieval confidence scoring for quality-aware RAG.
"""

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rank_bm25 import BM25Okapi
import logging
import re

from .documents import IT_KNOWLEDGE_BASE

logger = logging.getLogger(__name__)


def _tokenize(text: str) -> list:
    """Simple tokenizer for BM25: lowercase, split on non-alpha, remove stopwords."""
    tokens = re.findall(r'\b[a-z0-9]+\b', text.lower())
    stopwords = {
        'the', 'a', 'an', 'is', 'it', 'in', 'on', 'to', 'for', 'of', 'and',
        'or', 'not', 'with', 'as', 'at', 'by', 'be', 'are', 'was', 'were',
        'this', 'that', 'from', 'has', 'have', 'had', 'do', 'does', 'did',
        'but', 'if', 'you', 'your', 'we', 'our', 'they', 'their', 'i', 'my',
    }
    return [t for t in tokens if t not in stopwords and len(t) > 1]


class VectorStore:
    """In-memory vector store using TF-IDF + BM25 hybrid search."""

    def __init__(self):
        self.vectorizer = TfidfVectorizer(
            max_features=5000,
            stop_words='english',
            ngram_range=(1, 2),
            sublinear_tf=True
        )
        self.documents = []
        self.vectors = None
        self.bm25 = None
        self.bm25_corpus = []
        self.is_indexed = False

    def index_documents(self, documents=None):
        """Load, embed, and store documents in both vector and BM25 indexes."""
        if documents is None:
            documents = IT_KNOWLEDGE_BASE

        self.documents = documents

        texts = [
            f"{doc['title']} {' '.join(doc.get('tags', []))} {doc['content']}"
            for doc in documents
        ]

        # TF-IDF vectors
        self.vectors = self.vectorizer.fit_transform(texts)

        # BM25 index
        self.bm25_corpus = [_tokenize(t) for t in texts]
        self.bm25 = BM25Okapi(self.bm25_corpus)

        self.is_indexed = True
        logger.info(f"Indexed {len(documents)} documents (TF-IDF + BM25)")
        return len(documents)

    def search(self, query, top_k=5, min_score=0.05):
        """Hybrid retrieval: combine cosine similarity and BM25 scores."""
        from config.constants import HYBRID_SEARCH

        if not self.is_indexed:
            self.index_documents()

        n = len(self.documents)
        use_hybrid = HYBRID_SEARCH["enabled"] and self.bm25 is not None

        # TF-IDF cosine similarity
        query_vector = self.vectorizer.transform([query])
        cosine_scores = cosine_similarity(query_vector, self.vectors)[0]

        if use_hybrid:
            # BM25 scores
            query_tokens = _tokenize(query)
            bm25_scores = self.bm25.get_scores(query_tokens)

            # Normalize both to [0, 1]
            cos_max = cosine_scores.max() if cosine_scores.max() > 0 else 1.0
            bm25_max = bm25_scores.max() if bm25_scores.max() > 0 else 1.0
            norm_cos = cosine_scores / cos_max
            norm_bm25 = bm25_scores / bm25_max

            alpha = HYBRID_SEARCH["vector_weight"]
            beta = HYBRID_SEARCH["bm25_weight"]
            combined = alpha * norm_cos + beta * norm_bm25

            # Use combined for ranking, but report cosine as the retrieval_score
            # (cosine is the calibrated score used for confidence thresholds)
            top_indices = combined.argsort()[-top_k:][::-1]
        else:
            top_indices = cosine_scores.argsort()[-top_k:][::-1]

        results = []
        for idx in top_indices:
            cos_score = float(cosine_scores[idx])
            if cos_score >= min_score or (use_hybrid and float(combined[idx]) >= min_score):
                results.append({
                    "document": self.documents[idx],
                    "score": round(cos_score, 4),
                    "source": self.documents[idx].get("source", "Unknown"),
                    "title": self.documents[idx]["title"]
                })

        logger.info(f"Hybrid search for '{query[:50]}...' returned {len(results)} results")
        return results

    @staticmethod
    def compute_confidence(results: list) -> dict:
        """Compute retrieval confidence from search results.

        Returns:
            dict with retrieval_score (float) and retrieval_confidence_label (str).
        """
        from config.constants import RETRIEVAL_CONFIDENCE

        if not results:
            return {"retrieval_score": 0.0, "retrieval_confidence_label": "low"}

        top_score = results[0]["score"]

        if top_score >= RETRIEVAL_CONFIDENCE["high_threshold"]:
            label = "high"
        elif top_score >= RETRIEVAL_CONFIDENCE["medium_threshold"]:
            label = "medium"
        else:
            label = "low"

        return {"retrieval_score": round(top_score, 4), "retrieval_confidence_label": label}

    def get_document_count(self):
        """Return the number of indexed documents."""
        return len(self.documents)


# Singleton instance - initialized once at startup
vector_store = VectorStore()

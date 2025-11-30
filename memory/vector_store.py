"""Vector store for semantic search and memory retrieval."""

from typing import List, Dict, Any, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class VectorStore:
    """Simple vector store using TF-IDF for semantic search."""
    
    def __init__(self, storage_path: Optional[Path] = None):
        self.storage_path = storage_path or Path("memory/storage/vectors.json")
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.documents: List[Dict[str, Any]] = []
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.vectors: Optional[np.ndarray] = None
        
        self._load()
    
    def add_document(self, doc_id: str, text: str, metadata: Dict[str, Any] = None) -> None:
        """Add a document to the vector store."""
        
        doc = {
            "id": doc_id,
            "text": text,
            "metadata": metadata or {}
        }
        
        # Check for duplicates
        for i, existing in enumerate(self.documents):
            if existing["id"] == doc_id:
                self.documents[i] = doc
                self._rebuild_vectors()
                self._save()
                return
        
        self.documents.append(doc)
        self._rebuild_vectors()
        self._save()
        
        logger.info(f"Added document: {doc_id}")
    
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Search for similar documents."""
        
        if not self.documents or self.vectors is None:
            return []
        
        try:
            query_vector = self.vectorizer.transform([query])
            similarities = cosine_similarity(query_vector, self.vectors)[0]
            
            # Get top-k indices
            top_indices = np.argsort(similarities)[::-1][:top_k]
            
            results = []
            for idx in top_indices:
                if similarities[idx] > 0:
                    results.append({
                        "document": self.documents[idx],
                        "score": float(similarities[idx])
                    })
            
            return results
        
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific document by ID."""
        
        for doc in self.documents:
            if doc["id"] == doc_id:
                return doc
        
        return None
    
    def _rebuild_vectors(self) -> None:
        """Rebuild the vector index."""
        
        if not self.documents:
            self.vectors = None
            return
        
        texts = [doc["text"] for doc in self.documents]
        
        try:
            self.vectors = self.vectorizer.fit_transform(texts).toarray()
        except Exception as e:
            logger.error(f"Failed to rebuild vectors: {e}")
            self.vectors = None
    
    def _save(self) -> None:
        """Save documents to disk."""
        
        try:
            data = {
                "documents": self.documents
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save vector store: {e}")
    
    def _load(self) -> None:
        """Load documents from disk."""
        
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    self.documents = data.get("documents", [])
                    self._rebuild_vectors()
                    logger.info(f"Loaded {len(self.documents)} documents")
            except Exception as e:
                logger.warning(f"Failed to load vector store: {e}")

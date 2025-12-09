"""
Elasticsearch client wrapper with connection management and search methods
"""
from elasticsearch import Elasticsearch
from typing import Optional
from config import get_settings

settings = get_settings()


class ElasticsearchClient:
    """
    Wrapper class for Elasticsearch operations
    Manages connection and provides search methods
    """

    def __init__(self):
        """Initialize Elasticsearch client"""
        self.client = Elasticsearch(
            [settings.elasticsearch_url],
            request_timeout=30,
            max_retries=3,
            retry_on_timeout=True,
        )
        self.index_name = settings.elasticsearch_index

    def is_connected(self) -> bool:
        """
        Check if Elasticsearch is reachable
        Returns: True if connected, False otherwise
        """
        try:
            return self.client.ping()
        except Exception:
            return False

    def index_exists(self) -> bool:
        """
        Check if the product index exists
        Returns: True if index exists, False otherwise
        """
        try:
            return self.client.indices.exists(index=self.index_name)
        except Exception:
            return False

    def get_document_count(self) -> Optional[int]:
        """
        Get total number of documents in the index
        Returns: Document count or None if error
        """
        try:
            result = self.client.count(index=self.index_name)
            return result["count"]
        except Exception:
            return None

    def close(self):
        """Close Elasticsearch connection"""
        try:
            self.client.close()
        except Exception:
            pass

# Global client instance
_es_client: Optional[ElasticsearchClient] = None


def get_es_client() -> ElasticsearchClient:
    """
    Get or create global Elasticsearch client instance
    Returns: ElasticsearchClient instance
    """
    global _es_client
    if _es_client is None:
        _es_client = ElasticsearchClient()
    return _es_client


def close_es_client():
    """Close global Elasticsearch client"""
    global _es_client
    if _es_client is not None:
        _es_client.close()
        _es_client = None

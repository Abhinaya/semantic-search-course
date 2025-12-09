"""
Pydantic models for API request/response validation
"""
from pydantic import BaseModel, Field
from typing import List, Optional


class SearchRequest(BaseModel):
    """Request model for search endpoints"""

    query: str = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Search query string",
        examples=["bluetooth headphones"],
    )
    size: Optional[int] = Field(
        default=10,
        ge=1,
        le=100,
        description="Number of results to return (1-100)",
    )

    class Config:
        json_schema_extra = {
            "example": {
                "query": "wireless headphones",
                "size": 10,
            }
        }


class Product(BaseModel):
    """Single product search result"""

    id: int = Field(..., description="Product ID")
    title: str = Field(..., description="Product title")
    description: str = Field(..., description="Product description")
    score: float = Field(..., description="Relevance score from Elasticsearch")

    class Config:
        json_schema_extra = {
            "example": {
                "id": 123,
                "title": "Sony WH-1000XM5 Wireless Headphones",
                "description": "Premium noise-canceling wireless headphones with 30-hour battery life",
                "score": 15.234,
            }
        }


class SearchResponse(BaseModel):
    """Response model for search endpoints"""

    query: str = Field(..., description="Original search query")
    total_hits: int = Field(..., description="Total number of matching documents")
    results: List[Product] = Field(
        default=[], description="List of matching products"
    )
    took_ms: int = Field(..., description="Search execution time in milliseconds")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "wireless headphones",
                "total_hits": 45,
                "results": [
                    {
                        "id": 123,
                        "title": "Sony WH-1000XM5 Wireless Headphones",
                        "description": "Premium noise-canceling wireless headphones",
                        "score": 15.234,
                    }
                ],
                "took_ms": 42,
            }
        }


class ErrorResponse(BaseModel):
    """Error response model"""

    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

"""
FastAPI Product Search API - Day 1: Keyword Search (BM25)

This is the main application entry point for the 7-day bootcamp.
Day 1 focuses on building a basic REST API with BM25 keyword search.
"""
from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from config import get_settings
from models import (
    SearchRequest,
    SearchResponse,
    ErrorResponse,
)
from elasticsearch_client import get_es_client, close_es_client

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifecycle manager for FastAPI app
    Handles startup and shutdown events
    """
    # Startup: Test Elasticsearch connection
    es_client = get_es_client()
    if not es_client.is_connected():
        print("⚠️  Warning: Cannot connect to Elasticsearch")
    else:
        print("✅ Connected to Elasticsearch")
        if es_client.index_exists():
            doc_count = es_client.get_document_count()
            print(f"✅ Index '{settings.elasticsearch_index}' exists with {doc_count} documents")
        else:
            print(f"⚠️  Warning: Index '{settings.elasticsearch_index}' does not exist")

    yield

    # Shutdown: Close Elasticsearch connection
    close_es_client()
    print("👋 Closed Elasticsearch connection")


# Initialize FastAPI app
app = FastAPI(
    title="Product Search API",
    description="Bootcamp: Product Search + RAG Q&A Application",
    version="1.0.0",
    lifespan=lifespan,
)

# Add CORS middleware to allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/", tags=["Root"])
async def root():
    """
    Root endpoint
    """
    return {
        "message": "Product Search",
        "version": "1.0.0",
    }


@app.post(
    "/search",
    response_model=SearchResponse,
    responses={
        200: {"description": "Search successful"},
        500: {"model": ErrorResponse, "description": "Search failed"},
    },
    tags=["Search"],
)
async def search_products(request: SearchRequest):
    """
    Performs lexical/keyword search
    """
    es_client = get_es_client()

    # Verify Elasticsearch is available
    if not es_client.is_connected():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Elasticsearch is not available",
        )

    if not es_client.index_exists():
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Index '{settings.elasticsearch_index}' does not exist. "
            "Please run indexing script first.",
        )

    try:
        products = []

        return SearchResponse(
            query=request.query,
            total_hits=0,
            results=products,
            took_ms=0,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Search failed: {str(e)}",
        )

if __name__ == "__main__":
    import uvicorn

    print(f"""
    🚀 Starting Product Search API

    📍 Server: http://{settings.api_host}:{settings.api_port}
    📚 API Docs: http://{settings.api_host}:{settings.api_port}/docsx

    Press CTRL+C to quit
    """)

    uvicorn.run(
        "main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=True,  # Auto-reload on code changes
    )

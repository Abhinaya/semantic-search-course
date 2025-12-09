"""
Index products to Elasticsearch with embeddings
Can be run standalone or via Docker
"""
import sys
import csv
from pathlib import Path
from elasticsearch import Elasticsearch
from sentence_transformers import SentenceTransformer
from config import get_settings

settings = get_settings()

# Index configuration
INDEX_NAME = settings.elasticsearch_index
EMBEDDING_MODEL = "all-MiniLM-L6-v2"


def create_index(es_client: Elasticsearch) -> bool:
    """Create the Elasticsearch index with mappings"""

    # Delete index if it exists
    if es_client.indices.exists(index=INDEX_NAME):
        print(f"⚠️  Index '{INDEX_NAME}' already exists. Deleting...")
        es_client.indices.delete(index=INDEX_NAME)

    # Create index with mappings
    mapping = {
        "mappings": {
            "properties": {
                "id": {"type": "integer"},
                "title": {"type": "text"},
                "description": {"type": "text"},
                "embedding": {
                    "type": "dense_vector",
                    "dims": 384,
                    "index": True,
                    "similarity": "cosine",
                },
            }
        }
    }

    es_client.indices.create(index=INDEX_NAME, body=mapping)
    print(f"✅ Created index '{INDEX_NAME}'")
    return True


def load_products(csv_path: Path) -> list:
    """Load products from CSV file"""
    products = []

    with open(csv_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            products.append({
                "id": int(row["id"]),
                "title": row["TITLE"],
                "description": row["DESCRIPTION"],
            })

    print(f"✅ Loaded {len(products)} products from CSV")
    return products


def index_products(es_client: Elasticsearch, products: list, model: SentenceTransformer):
    """Index products with embeddings to Elasticsearch"""

    print(f"🔄 Generating embeddings and indexing {len(products)} products...")

    # Prepare bulk index data
    bulk_data = []

    for i, product in enumerate(products):
        # Combine title and description for embedding
        text = f"{product['title']} {product['description']}"

        # Generate embedding
        embedding = model.encode(text, normalize_embeddings=True).tolist()

        # Add to bulk data
        bulk_data.append({"index": {"_index": INDEX_NAME, "_id": product["id"]}})
        bulk_data.append({
            "id": product["id"],
            "title": product["title"],
            "description": product["description"],
            "embedding": embedding,
        })

        # Progress indicator
        if (i + 1) % 100 == 0:
            print(f"   Processed {i + 1}/{len(products)} products...")

    # Bulk index
    from elasticsearch.helpers import bulk

    actions = []
    for i in range(0, len(bulk_data), 2):
        action = bulk_data[i]
        doc = bulk_data[i + 1]
        actions.append({
            "_index": INDEX_NAME,
            "_id": doc["id"],
            "_source": doc,
        })

    success, failed = bulk(es_client, actions, refresh=True)
    print(f"✅ Indexed {success} products successfully")

    if failed:
        print(f"⚠️  Failed to index {len(failed)} products")

    return success


def main():
    """Main indexing function"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         Product Indexing Script                           ║
    ║         Index products with embeddings to Elasticsearch   ║
    ╚═══════════════════════════════════════════════════════════╝
    """)

    # Find CSV file (try multiple locations)
    csv_locations = [
        Path("../data/amazon_product_reviews_1000_utf8.csv"),  # From product-search-app
        Path("/data/amazon_product_reviews_1000_utf8.csv"),     # Docker volume
        Path("data/amazon_product_reviews_1000_utf8.csv"),      # From project root
    ]

    csv_path = None
    for path in csv_locations:
        if path.exists():
            csv_path = path
            print(f"📁 Found CSV file at: {csv_path}")
            break

    if csv_path is None:
        print("❌ Error: Could not find CSV file")
        print("   Tried locations:")
        for loc in csv_locations:
            print(f"   - {loc.absolute()}")
        sys.exit(1)

    # Connect to Elasticsearch
    print(f"🔌 Connecting to Elasticsearch at {settings.elasticsearch_url}...")
    es_client = Elasticsearch(
        [settings.elasticsearch_url],
        request_timeout=30,
        max_retries=3,
        retry_on_timeout=True,
    )

    if not es_client.ping():
        print(f"❌ Error: Cannot connect to Elasticsearch at {settings.elasticsearch_url}")
        sys.exit(1)

    print("✅ Connected to Elasticsearch")

    # Load embedding model
    print(f"🤖 Loading embedding model: {EMBEDDING_MODEL}...")
    model = SentenceTransformer(EMBEDDING_MODEL)
    print("✅ Model loaded")

    # Create index
    create_index(es_client)

    # Load products
    products = load_products(csv_path)

    # Index products with embeddings
    indexed_count = index_products(es_client, products, model)

    # Verify
    doc_count = es_client.count(index=INDEX_NAME)["count"]
    print(f"\n✅ Indexing complete! Total documents in index: {doc_count}")

    # Show example
    print("\n🔍 Example document:")
    result = es_client.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 1})
    if result["hits"]["hits"]:
        doc = result["hits"]["hits"][0]["_source"]
        print(f"   ID: {doc['id']}")
        print(f"   Title: {doc['title']}")
        print(f"   Description: {doc['description'][:100]}...")
        print(f"   Embedding dims: {len(doc['embedding'])}")

    print("\n🎉 All done! You can now use the search API.")


if __name__ == "__main__":
    main()

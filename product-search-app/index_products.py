"""
Index products to Elasticsearch
Loads product data from CSV and creates searchable index
"""
import sys
import csv
from pathlib import Path
from elasticsearch import Elasticsearch
from config import get_settings

settings = get_settings()

# Index configuration
INDEX_NAME = settings.elasticsearch_index


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


def index_products(es_client: Elasticsearch, products: list):
    """Index products to Elasticsearch"""

    print(f"🔄 Indexing {len(products)} products...")

    # Prepare bulk index data
    from elasticsearch.helpers import bulk

    actions = []
    for product in products:
        actions.append({
            "_index": INDEX_NAME,
            "_id": product["id"],
            "_source": {
                "id": product["id"],
                "title": product["title"],
                "description": product["description"],
            }
        })

    # Bulk index
    success, failed = bulk(es_client, actions, refresh=True)
    print(f"✅ Indexed {success} products successfully")

    if failed:
        print(f"⚠️  Failed to index {len(failed)} products")

    return success


def main():
    """Main indexing function"""
    print("""
    ╔═══════════════════════════════════════════════════════════╗
    ║         Index products to Elasticsearch                   ║
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

    create_index(es_client)
    products = load_products(csv_path)
    index_products(es_client, products)

    doc_count = es_client.count(index=INDEX_NAME)["count"]
    print(f"\n✅ Indexing complete! Total documents in index: {doc_count}")


    print("\n🔍 Example document:")
    result = es_client.search(index=INDEX_NAME, body={"query": {"match_all": {}}, "size": 1})
    if result["hits"]["hits"]:
        doc = result["hits"]["hits"][0]["_source"]
        print(f"   ID: {doc['id']}")
        print(f"   Title: {doc['title']}")
        print(f"   Description: {doc['description'][:100]}...")

if __name__ == "__main__":
    main()

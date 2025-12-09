# 🔍 7-Day Bootcamp: Product Search + RAG Q&A Application

Build a production-ready semantic search and RAG Q&A system from scratch in 7 days.

**🎯 What You'll Build:**
- Day 1: ✅ Keyword Search (BM25) with FastAPI
- Day 2: Synonyms & Fuzzy Search
- Day 3: Semantic Search (Embeddings)
- Day 4: Vector Search (kNN)
- Day 5: Hybrid Search (BM25 + Vector)
- Day 6: RAG Q&A with LLM
- Day 7: Streamlit UI

**🛠 Tech Stack:**
- FastAPI for REST API
- Elasticsearch for search & vector storage
- SentenceTransformers for embeddings
- LLM for RAG (OpenAI/Groq)
- Docker for deployment

---

## 🚀 Quick Start (3 Commands)

```bash
# 1. Start all services (Elasticsearch + Kibana + FastAPI + Frontend)
docker-compose up -d --build

# 2. Index 1000 products (wait for services to be healthy first)
docker exec product-search-api python index_products.py

# 3. Access Search UI
open http://localhost:3000
```

**That's it!** 🎉 Your complete search application is running!

**🌐 Access Points:**
- **🎨 Search UI:** http://localhost:3000
- **📚 API Docs:** http://localhost:8000/docs
- **📊 Kibana:** http://localhost:5601

**📖 Detailed Setup:** See [DOCKER_SETUP.md](./DOCKER_SETUP.md) for complete Docker guide.

---

## 📦 Installation

### Option 1: Using Docker (Recommended)

Start Elasticsearch and Kibana using Docker Compose:

```bash
# Start the services
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

This will start:
- **Elasticsearch** on `http://localhost:9200`
- **Kibana** on `http://localhost:5601`

### Option 2: Manual Installation

Install dependencies using Poetry:

```bash
poetry install
```

## 🔐 Set Up Elasticsearch Credentials

### For Docker Setup
No credentials needed - security is disabled for development.

### For Manual Setup
Export your Elasticsearch credentials as environment variables:

```bash
export ES_USERNAME=<YOUR-ELASTICSEARCH-USERNAME>
export ES_PASSWORD=<YOUR-ELASTICSEARCH-PASSWORD>
```

Make sure your Elasticsearch instance is running and accessible (e.g. at http://localhost:9200).

---

## 🧠 Index Product Metadata to Elasticsearch

To index product data into Elasticsearch:

**Option 1: Docker (Recommended)**
```bash
docker exec product-search-api python index_products.py
```

**Option 2: Local with uv/poetry (with embeddings)**
```bash
# Using uv (includes embeddings for semantic search)
uv run src/elacticsearch_demo/step1_index_products.py

# Or using poetry
poetry run python src/elacticsearch_demo/step1_index_products.py
```

👉 **Option 1** (Docker) will:
- Read the data CSV file (1000 products)
- Create an Elasticsearch index named `amazon_products`
- Bulk index all records with title and description
- Takes ~5-10 seconds

👉 **Option 2** (Local script) will also:
- Generate vector embeddings using `all-MiniLM-L6-v2`
- Index with embeddings for semantic search
- Takes ~2-3 minutes

---

## 🐳 Docker Services

The `docker-compose.yml` includes:

- **Elasticsearch 9.0.3**: Vector search engine (port 9200)
- **Kibana 9.0.3**: Data visualization and management UI (port 5601)
- **Product Search API**: FastAPI application (port 8000)
- **Frontend UI**: Search interface with npx serve (port 3000)
- **Persistent storage**: Data persists between container restarts
- **Health checks**: Ensures services are ready before dependencies start
- **Auto-restart**: Services restart automatically on failure

### 🌐 Service URLs

- **🎨 Search UI:** http://localhost:3000 (Start here!)
- **Product Search API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Elasticsearch:** http://localhost:9200
- **Kibana:** http://localhost:5601

### Useful Docker Commands

```bash
# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes all data)
docker-compose down -v

# Restart services
docker-compose restart

# View service logs
docker-compose logs elasticsearch
docker-compose logs kibana
```

---

## 📚 Tech Stack

- Python 3.10+
- [Poetry](https://python-poetry.org/)
- Docker & Docker Compose
- Elasticsearch 8+
- Kibana 8+
- `sentence-transformers` (MiniLM-L6-v2)

---

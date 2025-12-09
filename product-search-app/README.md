# 🚀 Product Search API - 7-Day Bootcamp

A hands-on bootcamp to build a Product Search + RAG Q&A application from scratch.

---

## 📅 Day 1: Build the Base App (Keyword Search)

### 🎯 Goal
Get the skeleton of the application running with basic lexical search.

### 🏗 What You'll Build
- ✅ FastAPI project skeleton
- ✅ Connect to Elasticsearch
- ✅ Create `/search` endpoint with BM25
- ✅ Return top N product hits

## 🛠 Setup Instructions

### Prerequisites
- **Option A (Recommended):** Docker & Docker Compose only
- **Option B (Local Development):** Python 3.11+ and `uv` package manager

---

## 🐳 Setup Option A: Docker (Recommended)

**Everything runs in containers - Elasticsearch + Kibana + FastAPI backend + Frontend**

### Step 1: Start All Services
```bash
# Navigate to parent directory (semantic-search-course/)
cd ..

# Build and start all services (Elasticsearch, Kibana, FastAPI)
docker-compose up -d --build

# Wait ~30 seconds for services to start, then check status
docker-compose ps
```

**Expected output:**
```
NAME                 STATUS         PORTS
es01                 healthy        0.0.0.0:9200->9200/tcp
kib01                healthy        0.0.0.0:5601->5601/tcp
product-search-api   healthy        0.0.0.0:8000->8000/tcp
```

### Step 2: Index Product Data
```bash
# Run indexing inside Docker container
docker exec product-search-api python index_products.py
```

**What it does:**
- Loads 1000 products from CSV
- Creates Elasticsearch index
- Indexes products with title and description
- Takes ~5-10 seconds

**Expected output:**
```
✅ Connected to Elasticsearch
✅ Created index 'amazon_products'
✅ Loaded 1000 products from CSV
🔄 Indexing 1000 products...
✅ Indexed 1000 products successfully
🎉 All done!
```

### Step 3: Access the Services

**🎉 That's it! All services are now running:**

- **🎨 Search UI:** http://localhost:3000 **(Start here!)**
- **Product Search API:** http://localhost:8000
- **API Documentation:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health
- **Elasticsearch:** http://localhost:9200
- **Kibana:** http://localhost:5601

### Step 4: Use the Search UI

**Open http://localhost:3000 in your browser**

Try these searches:
- `wireless headphones` - See highlighted terms in results
- `Sony headphones` - Exact brand match
- `running shoes` - Multiple matches
- `coffee maker` - Kitchen products

**Features:**
- 🔍 Real-time search as you type
- 🎨 Search terms highlighted in yellow
- 📊 Relevance scores (BM25) displayed
- 📱 Mobile-responsive design

**Or test via API** - Jump to the [Test the API](#-test-the-api) section below.

### Docker Management Commands

```bash
# View logs
docker-compose logs -f product-search-app
docker-compose logs -f elasticsearch

# Restart a service
docker-compose restart product-search-app

# Re-index products (delete and recreate index)
docker exec product-search-api python index_products.py

# Check index status
curl http://localhost:9200/amazon_products/_count

# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (deletes all data)
docker-compose down -v

# Rebuild after code changes
docker-compose up -d --build product-search-app
```

---

## 💻 Setup Option B: Local Development

**Run FastAPI locally, Elasticsearch in Docker**

### Step 1: Start Elasticsearch & Kibana
```bash
# Navigate to parent directory
cd ..

# Start only Elasticsearch and Kibana
docker-compose up -d elasticsearch kibana

# Verify services are running
docker-compose ps
```

### Step 2: Index Product Data
```bash
# Index 1000 products with embeddings
uv run src/elacticsearch_demo/step1_index_products.py
```

### Step 3: Install Dependencies
```bash
# Navigate to product-search-app
cd product-search-app

# Install dependencies with uv
uv sync
```

### Step 4: Configure Environment
```bash
# Copy example env file
cp .env.example .env

# Edit .env if needed (default values should work)
# ELASTICSEARCH_URL=http://localhost:9200
# ELASTICSEARCH_INDEX=amazon_products
```

### Step 5: Run the API Locally
```bash
# Option 1: Using uv
uv run uvicorn main:app --reload

# Option 2: Using Python directly
python main.py

# Option 3: With custom host/port
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 💡 Day 1 Stretch Goals

### 1. Add Pagination
Add offset/from parameters to paginate results:

```python
class SearchRequest(BaseModel):
    query: str
    size: int = 10
    from_: int = 0  # New field for pagination
```

### 2. Add Field Boosting
Make title matches more important than description:

```python
"fields": ["title^3", "description"]  # 3x boost for title
```

# 🐳 Docker Setup Guide

Complete guide for running the entire Product Search + RAG application using Docker Compose.

---

## 📦 What's Included

The Docker Compose setup includes:

1. **Elasticsearch 9.0.3** - Vector search engine (port 9200)
2. **Kibana 9.0.3** - Data visualization UI (port 5601)
3. **Product Search API** - FastAPI application (port 8000)

All services are connected via Docker network and include health checks.

---

## 🚀 Quick Start (3 Steps)

### 1. Start All Services

```bash
# Clone or navigate to project directory
cd semantic-search-course/

# Start everything with one command
docker-compose up -d --build

# Wait 30-60 seconds for services to become healthy
docker-compose ps
```

**Expected output:**
```
NAME                 STATUS         PORTS
es01                 healthy        0.0.0.0:9200->9200/tcp
kib01                healthy        0.0.0.0:5601->5601/tcp
product-search-api   healthy        0.0.0.0:8000->8000/tcp
```

### 2. Index Product Data

```bash
# Index 1000 products (run once)
uv run src/elacticsearch_demo/step1_index_products.py
```

### 3. Access Services

- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs
- **Kibana:** http://localhost:5601
- **Elasticsearch:** http://localhost:9200

---

## 🎯 Service Details

### Elasticsearch (es01)

- **Image:** `docker.elastic.co/elasticsearch/elasticsearch:9.0.3`
- **Port:** 9200
- **Memory:** 512MB - 1GB
- **Features:**
  - Single-node cluster
  - Security disabled (dev mode)
  - Persistent storage volume
  - Health check on cluster health

**Direct Access:**
```bash
# Check cluster health
curl http://localhost:9200/_cluster/health?pretty

# List indices
curl http://localhost:9200/_cat/indices?v

# Search products
curl http://localhost:9200/amazon_products/_search?pretty
```

### Kibana (kib01)

- **Image:** `docker.elastic.co/kibana/kibana:9.0.3`
- **Port:** 5601
- **Features:**
  - Connected to Elasticsearch
  - Dev Tools console
  - Index Management UI
  - Health check on status API

**Useful URLs:**
- Dev Tools: http://localhost:5601/app/dev_tools#/console
- Index Management: http://localhost:5601/app/management/data/index_management

### Product Search API (product-search-api)

- **Build:** Custom Dockerfile (FastAPI + uv)
- **Port:** 8000
- **Features:**
  - Auto-connects to Elasticsearch via Docker network
  - Environment-based configuration
  - Health check on `/health` endpoint
  - Auto-restart on failure

**Endpoints:**
- Root: http://localhost:8000/
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health
- Search: http://localhost:8000/search (POST)

---

## 🔧 Configuration

### Environment Variables

The FastAPI app uses these environment variables (set in docker-compose.yml):

```yaml
ELASTICSEARCH_URL: http://es01:9200        # Internal Docker network
ELASTICSEARCH_INDEX: amazon_products
API_HOST: 0.0.0.0
API_PORT: 8000
DEFAULT_SEARCH_SIZE: 10
```

**Note:** Inside Docker, Elasticsearch is accessed via `es01:9200` (container name), not `localhost:9200`.

### Network Configuration

All services are connected via the `elastic` bridge network:

```
elastic network
├── es01 (Elasticsearch)
├── kib01 (Kibana) → connects to es01:9200
└── product-search-api → connects to es01:9200
```

This allows services to communicate using container names as hostnames.

---

## 📋 Common Commands

### Viewing Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f product-search-api
docker-compose logs -f elasticsearch
docker-compose logs -f kibana

# Last 50 lines
docker-compose logs --tail=50 product-search-api
```

### Restarting Services

```bash
# Restart single service
docker-compose restart product-search-api

# Restart all services
docker-compose restart

# Restart after code changes (rebuild)
docker-compose up -d --build product-search-app
```

### Stopping Services

```bash
# Stop all services (keeps data)
docker-compose down

# Stop and remove volumes (deletes data)
docker-compose down -v

# Stop single service
docker-compose stop product-search-api
```

### Service Status

```bash
# Check status of all services
docker-compose ps

# Check health status
docker-compose ps --format json | jq '.[].Health'

# View resource usage
docker stats
```

### Executing Commands Inside Containers

```bash
# Shell into FastAPI container
docker exec -it product-search-api sh

# Shell into Elasticsearch container
docker exec -it es01 bash

# Run Python command in FastAPI container
docker exec product-search-api python -c "import sys; print(sys.version)"
```

---

## 🐛 Troubleshooting

### Service Won't Start

**Check logs:**
```bash
docker-compose logs elasticsearch
docker-compose logs product-search-app
```

**Common issues:**
- Port already in use (8000, 9200, 5601)
- Insufficient memory for Elasticsearch
- Docker daemon not running

**Solution:**
```bash
# Check what's using port 8000
lsof -i :8000

# Increase Docker memory to 4GB+ in Docker Desktop settings
```

### Elasticsearch Unhealthy

**Check status:**
```bash
docker-compose ps
docker-compose logs elasticsearch
curl http://localhost:9200/_cluster/health?pretty
```

**Solution:**
```bash
# Restart Elasticsearch
docker-compose restart elasticsearch

# Or recreate
docker-compose down
docker-compose up -d
```

### FastAPI Can't Connect to Elasticsearch

**Verify network:**
```bash
# Check if es01 is resolvable from FastAPI container
docker exec product-search-api ping es01 -c 2

# Check if Elasticsearch is healthy
docker-compose ps elasticsearch
```

**Solution:**
```bash
# Restart with proper dependency
docker-compose down
docker-compose up -d
```

### Index Not Found

**Check if index exists:**
```bash
curl http://localhost:9200/_cat/indices?v
```

**Solution:**
```bash
# Run indexing script
uv run src/elacticsearch_demo/step1_index_products.py

# Verify
curl http://localhost:9200/amazon_products/_count
```

### Code Changes Not Reflected

**Rebuild the image:**
```bash
docker-compose up -d --build product-search-app

# Or force rebuild
docker-compose build --no-cache product-search-app
docker-compose up -d product-search-app
```

---

## 🔄 Development Workflow

### Making Code Changes

**With Docker:**
```bash
# 1. Edit code in product-search-app/
vim product-search-app/main.py

# 2. Rebuild and restart
docker-compose up -d --build product-search-app

# 3. Test changes
curl http://localhost:8000/health
```

**With Local Development (faster):**
```bash
# 1. Stop Docker FastAPI service
docker-compose stop product-search-app

# 2. Run locally with hot reload
cd product-search-app
uv run uvicorn main:app --reload

# 3. Code changes auto-reload immediately

# 4. When done, restart Docker service
docker-compose up -d product-search-app
```

### Adding Dependencies

**Method 1: Update pyproject.toml and rebuild**
```bash
# 1. Edit pyproject.toml
vim product-search-app/pyproject.toml

# 2. Rebuild image
docker-compose build --no-cache product-search-app

# 3. Restart
docker-compose up -d product-search-app
```

**Method 2: Install in running container (temporary)**
```bash
docker exec product-search-api pip install new-package
docker-compose restart product-search-app
```

---

## 📊 Monitoring & Health Checks

### Health Check Endpoints

```bash
# FastAPI health
curl http://localhost:8000/health | jq

# Elasticsearch cluster health
curl http://localhost:9200/_cluster/health?pretty

# Kibana status
curl http://localhost:5601/api/status | jq
```

### Expected Healthy Response

**FastAPI `/health`:**
```json
{
  "status": "healthy",
  "elasticsearch_connected": true,
  "index_exists": true,
  "document_count": 1000
}
```

**Elasticsearch:**
```json
{
  "cluster_name": "docker-cluster",
  "status": "green",
  "number_of_nodes": 1
}
```

### Docker Health Status

```bash
# View health status
docker-compose ps

# Should show "healthy" for all services:
# es01                 healthy
# kib01                healthy
# product-search-api   healthy
```

---

## 💾 Data Persistence

### Elasticsearch Data

Data is stored in a named Docker volume: `esdata01`

```bash
# List volumes
docker volume ls | grep esdata

# Inspect volume
docker volume inspect semantic-search-course_esdata01

# Backup volume
docker run --rm -v semantic-search-course_esdata01:/data -v $(pwd):/backup alpine tar czf /backup/es-backup.tar.gz /data

# Restore volume
docker run --rm -v semantic-search-course_esdata01:/data -v $(pwd):/backup alpine tar xzf /backup/es-backup.tar.gz -C /
```

### Removing Data

```bash
# Remove all data and volumes
docker-compose down -v

# Remove specific volume
docker volume rm semantic-search-course_esdata01
```

---

## 🎓 Production Considerations

**⚠️ This setup is for DEVELOPMENT only. For production:**

1. **Enable Security:**
   - Enable Elasticsearch authentication
   - Use HTTPS/TLS
   - Set strong passwords

2. **Increase Resources:**
   - Elasticsearch: 4GB+ RAM
   - Multi-node cluster
   - Dedicated machine

3. **Add Load Balancer:**
   - Nginx/Traefik in front of FastAPI
   - Multiple FastAPI replicas

4. **Monitoring:**
   - Prometheus + Grafana
   - APM (Application Performance Monitoring)
   - Centralized logging (ELK stack)

5. **Backup Strategy:**
   - Regular Elasticsearch snapshots
   - Data replication
   - Disaster recovery plan

---

## 📚 Additional Resources

- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [Elasticsearch Docker Guide](https://www.elastic.co/guide/en/elasticsearch/reference/current/docker.html)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

## 🆘 Getting Help

**If you encounter issues:**

1. Check logs: `docker-compose logs -f`
2. Verify health: `docker-compose ps`
3. Test connectivity: `curl http://localhost:8000/health`
4. Review this troubleshooting guide
5. Check GitHub issues

**Common commands summary:**
```bash
# Start everything
docker-compose up -d --build

# Check status
docker-compose ps

# View logs
docker-compose logs -f product-search-app

# Restart service
docker-compose restart product-search-app

# Stop everything
docker-compose down

# Nuclear option (remove everything)
docker-compose down -v
docker system prune -a
```

---

**Happy Dockering! 🐳**

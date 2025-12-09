---
marp: true
theme: gaia
paginate: true
class: invert
style: |
  section {
    font-size: 28px;
  }
  section h2 {
    font-size: 42px;
  }
  section pre {
    font-size: 20px;
  }
  section code {
    font-size: 22px;
  }
  section ul, section ol {
    font-size: 26px;
  }
---

**Bootcamp: Product Search + RAG Q&A**

---

### What are we building?

 An application that can search through a catalog of products

---

### How do we build ?

- SQL ?
- Custom search solution ?
- Existing Search tools/engines ?

---

## Why Elasticsearch?

**What is it?**

- Distributed search & analytics engine
- Built on Apache Lucene
- Supports structured & unstructured data

**Why we need it:**

- Fast full-text search
- Real-time indexing
- Scalable across multiple nodes
- JSON-based REST API

---

### Today's Goal

Build a working application with basic **lexical search**

By the end of today, you'll have:
- ✅ Elasticsearch connection with 1000 products data indexed
- ✅ FastAPI skeleton running
- ✅ Basic search UI
- ✅ `/search` endpoint
- ✅ Top 10 product results

---

## Elastic Stack Architecture

**Components of the Elastic Stack**

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   INGEST    │     │ CONSOLIDATE │     │    STORE    │     │   CONSUME   │
├─────────────┤     ├─────────────┤     ├─────────────┤     ├─────────────┤
│             │     │             │     │             │     │             │
│ • Beats     │     │ • Logstash  │     │Elasticsearch│     │ • Kibana    │
│ • Agents    │     │ • Pipelines │     │             │     │             │
│ • APM       │     │ • Transform │     │  - Index    │     │ • Clients   │
│ • Apps      │     │ • Enrich    │     │  - Store    │     │ • APIs      │
│             │     │             │     │  - Search   │     │ • Dashboards│
│             │     │             │     │  - Analyze  │     │             │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
       │                   │                   │                  │
       └───────►───────────┴────────►──────────┴────────◄────►────┘

     Collect            Process            Index             Visualize
      Data               Data             & Search            Results
```

---

### 1. What is an Index?

Think of it as a **database table** for documents

```
Index: amazon_products
├── Document 1: {id: 1, title: "Headphones", ...}
├── Document 2: {id: 2, title: "Shoes", ...}
└── Document 3: {id: 3, title: "Laptop", ...}
```

---

### 2. What is a Document?

A **single record** in the index (JSON format)

```json
{
  "id": 123,
  "title": "Sony WH-1000XM5 Wireless Headphones",
  "description": "Premium noise-canceling wireless..."
}
```
---

### Tokenization

Elasticsearch breaks text into **tokens** (individual words)

**Example:**

```
Original Text:
"Sony WH-1000XM5 Wireless Headphones"

After Tokenization:
["sony", "wh", "1000", "xm5", "wireless", "headphones"]

How it is stored:
wireless → doc1, doc7, doc22
sony → doc1, doc3
headphone → doc1, doc2, doc9
```

✅ Lowercase conversion
✅ Split on spaces and special characters
✅ Each token is searchable independently

---

### How Tokenization Enables Search

**Document in Index:**
```
"Sony WH-1000XM5 Wireless Headphones"
         ↓ tokenized ↓
["sony", "wh", "1000", "xm5", "wireless", "headphones"]
```

**Your Query:**
```
"wireless headphones"
         ↓ tokenized ↓
["wireless", "headphones"]
```

**Matching:**
```
Document tokens: ["sony", "wh", "1000", "xm5", "wireless", "headphones"]
                                             ✅ MATCH    ✅ MATCH
Query tokens:                          ["wireless", "headphones"]
```

**Result:** ✅ Document found! 2 out of 2 query tokens matched

---

### Relevance & Ranking

```
🔍 Query: "wireless headphones"
                     
📄Document A: "Sony Wireless Headphones Premium"
- wireless    ✔ (1 match)
- headphones  ✔ (1 match)
- ✅ Short document (4 words) → higher relevance
🎯 Score: 18.5

📄Document B: "Best Wireless Audio Equipment for Home"
- wireless    ✔ (1 match)
- headphones  ✘ (0 match)
- ⚠️  Longer document (6 words) → lower relevance
🎯 Score: 6.2

📄Document C: "Premium Bluetooth Speaker"
- wireless    ✘
- headphones  ✘
🎯 Score: 0.0 (not returned)
```

**Ranking Order:** A (18.5) → B (6.2) → C (not shown)

---

### BM25 is the algorithm

**Best Matching 25** - A probabilistic ranking algorithm. Finds documents with your query words and ranks by relevance

**Key factors:**
- **Term Frequency (TF)**: How often words appear in document
- **Inverse Document Frequency (IDF)**: Rarity of terms. If a term appears in every doc often, it's scored low. (eg. the, good)
- **Document Length**: Normalize for long docs

Used by all Lucene based search tools - ElasticSearch, Solr, OpenSearch. 
Amazon product search initially used BM25.

---

### Try These Queries

**Queries that WORK well with BM25:**

1. `"Sony headphones"` → Exact brand match ✅
2. `"running shoes"` → Clear keywords ✅
3. `"stainless steel"` → Technical terms ✅

**Queries that FAIL with BM25:**

1. `"couch"` → Won't find "sofa" ❌
2. `"bluetoth"` → Typo fails ❌
3. `"keep coffee hot"` → No semantic understanding ❌

---

**Questions?**

---

**Happy Coding!** 🎉

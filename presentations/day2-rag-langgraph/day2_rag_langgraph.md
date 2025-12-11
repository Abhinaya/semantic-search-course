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

**Day 2: RAG & LangGraph**

# Retrieval-Augmented Generation (RAG)
#### Empowering LLMs with Real-World, Up-to-Date Knowledge

---

## The Problem with LLMs Alone

LLMs are powerful but have limitations
  - Knowledge is frozen (training cut-off)
  - Cannot access private or recent data
  - Can hallucinate answers when unsure

**Example:**
> Q: Can Khadims Black Slip-On Shoes be washed with deteregent?
> GPT: I'm not familiar with the specific material or care instructions for Khadims Black Slip-On Shoe...

---

##  Enter RAG: Retrieval-Augmented Generation

- Combines search + generation
- Bridges LLMs with your data

### How it works

1. Retrieve relevant docs (e.g. from Elasticsearch)
2. Pass them into the LLM as context
3. LLM generates grounded answers

---
## Real Use Case: E-commerce Product QA

- Corpus: 1000 product reviews
- User question: "Can Khadims Black Slip-On Shoes be washed with deteregent?"

#### Without RAG
vague answer or hallucination

#### With RAG
uses actual product review: "Do not wash with detergent or in washing machine"

---

# Architecture Overview

```
User Query
   |
[Retriever: Elasticsearch]
   |
Relevant Documents
   |
[LLM: Groq / GPT / Claude / Mistral]
   |
Generated Answer (grounded in facts)
```

---

## RAG Example Flow

**User:** "I need noise canceling headphones for travel"

**Step 1 - Retrieve:**
```python
search_results = elasticsearch.search(
    query="noise canceling headphones travel"
)
# Returns: Sony WH-1000XM5, Bose QC45, etc.
```

**Step 2 - Augment:**
```python
context = format_results_as_context(search_results)
prompt = f"""Based on these products:
{context}

User question: {user_query}
Recommend the best option and explain why."""
```

**Step 3 - Generate:**
```python
answer = llm.generate(prompt)
```

---

## What is LangGraph?

A framework for building **stateful, multi-step agents**

**Key Concepts:**
- **Nodes:** Individual steps/functions in the workflow
- **Edges:** Transitions between nodes
- **State:** Data that flows through the graph
- **Graph:** The complete workflow

Built on top of LangChain, designed for complex agent workflows

---

## LangGraph

**LangGraph Agent:**
```
User → Plan → Search → Analyze → Respond
         ↓      ↓        ↓
      [State Management]
         ↑      ↑        ↑
    Loop back if needed
```

**Benefits:**
- Multi-step reasoning
- Tool calling (search, calculate, etc.)
- Error handling & retry logic
- Human-in-the-loop
- Conversation memory

---

## LangGraph Core Concepts

**1. State:**
```python
class AgentState(TypedDict):
    messages: List[Message]
    query: str
    search_results: List[Dict]
    answer: str
```

**2. Nodes (Functions):**
```python
def search_products(state: AgentState):
    results = call_search_api(state["query"])
    return {"search_results": results}

def generate_answer(state: AgentState):
    answer = llm.invoke(state["search_results"])
    return {"answer": answer}
```

---

## LangGraph Core Concepts (cont.)

**3. Graph:**
```python
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("search", search_products)
workflow.add_node("generate", generate_answer)

# Add edges (flow)
workflow.add_edge("search", "generate")
workflow.add_edge("generate", END)

# Compile
app = workflow.compile()
```

---

## Simple LangGraph Flow

```
          START
            ↓
      ┌──────────┐
      │  Parse   │
      │  Query   │
      └────┬─────┘
           ↓
      ┌──────────┐
      │  Search  │
      │ Products │
      └────┬─────┘
           ↓
      ┌──────────┐
      │ Generate │
      │  Answer  │
      └────┬─────┘
           ↓
          END
```

---

## RAG + LangGraph Together

**RAG provides:** The pattern (Retrieve → Augment → Generate)
**LangGraph provides:** The orchestration framework

```python
# Node 1: Retrieve (RAG step 1)
def retrieve(state):
    results = elasticsearch.search(state["query"])
    return {"documents": results}

# Node 2: Generate (RAG step 2 & 3)
def generate(state):
    context = state["documents"]
    answer = llm.generate_with_context(context, state["query"])
    return {"answer": answer}

# Build graph
workflow.add_node("retrieve", retrieve)
workflow.add_node("generate", generate)
workflow.add_edge("retrieve", "generate")
```

---

## What is Chainlit?

**An open-source Python framework for building conversational AI applications**

**Key Features:**
- 🎨 **Chat UI**: Built-in beautiful chat interface
- 🔄 **Real-time**: Streaming responses and updates
- 📊 **Step Visibility**: Show intermediate steps to users
- 🔌 **LangChain Integration**: Works seamlessly with LangGraph
- 🐳 **Easy Deploy**: Docker-ready, production-grade

**Why Chainlit for agents?**
- Shows agent thinking process
- Better UX than plain API endpoints
- Built for conversational AI workflows

---

## Today's Goal

Build a RAG Agent with Chainlit that:

✅ Provides a chat interface for users
✅ Uses LangGraph to orchestrate workflow
✅ Searches products via our FastAPI backend
✅ Generates intelligent answers using LLM
✅ Shows thinking process to users

**Tech Stack:**
- Chainlit for chat UI
- LangGraph for agent orchestration
- Groq (llama-3.3-70b) for LLM
- FastAPI /search endpoint from Day 1

---

**Today's Implementation:**
- Create Chainlit chat interface
- Build LangGraph workflow with 2 nodes:
  - Node 1: Search products (calls FastAPI)
  - Node 2: Generate answer (calls LLM)

---

**Questions?**

---

**Let's Build!** 🚀

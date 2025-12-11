import os
import logging
from typing import TypedDict, List
import chainlit as cl
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
import httpx

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class AgentState(TypedDict):
    """State that flows through the LangGraph"""
    query: str
    search_results: List[dict]
    answer: str
    error: str | None


def get_llm():
    """Get Groq LLM instance"""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY not found in environment variables")

    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=0.7,
        api_key=api_key
    )


# Node 1: Search products
async def search_products(state: AgentState) -> AgentState:
    """
    Search for products using the /search API
    """
    query = state["query"]
    logger.info(f"🔍 Searching for: {query}")

    # Use environment variable for API URL (Docker service name or localhost)
    api_url = os.getenv("SEARCH_API_URL", "http://localhost:8000")
    logger.info(f"📡 API URL: {api_url}")

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{api_url}/search",
                json={"query": query, "size": 5},
                timeout=10.0
            )

            if response.status_code == 200:
                data = response.json()
                state["search_results"] = data["results"]
                logger.info(f"✅ Found {len(data['results'])} products in {data['took_ms']}ms")
            else:
                state["error"] = f"Search failed with status {response.status_code}"
                logger.error(f"❌ Search failed: {response.status_code}")

    except Exception as e:
        state["error"] = f"Search error: {str(e)}"
        logger.error(f"❌ Search error: {str(e)}")

    return state


# Node 2: Generate answer using LLM
async def generate_answer(state: AgentState) -> AgentState:
    """
    Generate answer using LLM with search results as context
    """
    if state.get("error"):
        state["answer"] = f"Sorry, I encountered an error: {state['error']}"
        logger.error(f"❌ Skipping LLM generation due to error: {state['error']}")
        return state

    search_results = state["search_results"]
    query = state["query"]

    if not search_results:
        state["answer"] = "I couldn't find any products matching your query. Could you try rephrasing?"
        logger.warning("⚠️ No search results found")
        return state

    logger.info(f"🤖 Generating answer using {len(search_results)} products as context")

    # Format search results as context
    context = "\n\n".join([
        f"Product {i+1}:\n"
        f"Title: {result['title']}\n"
        f"Description: {result['description']}\n"
        f"Relevance Score: {result['score']:.2f}"
        for i, result in enumerate(search_results)
    ])

    # Create prompt for LLM
    prompt = f"""You are a helpful product search assistant. Based on the search results below, answer the user's question accurately.

Search Results:
{context}

User Question: {query}

Instructions:
- Provide a concise answer
- Reference specific products from the search results
- If multiple products match, compare them briefly
- Be conversational
- If no products perfectly match, suggest the closest alternatives

Answer:"""

    try:
        logger.info("📝 Calling LLM (llama-3.3-70b-versatile)...")
        llm = get_llm()
        response = llm.invoke(prompt)
        state["answer"] = response.content
        logger.info(f"✅ Generated answer ({len(response.content)} chars)")
    except Exception as e:
        state["answer"] = f"Sorry, I couldn't generate a response: {str(e)}"
        logger.error(f"❌ LLM error: {str(e)}")

    return state


def create_agent_graph():
    """
    Create the LangGraph workflow for RAG
    """
    workflow = StateGraph(AgentState)

    # Add nodes
    workflow.add_node("search", search_products)
    workflow.add_node("generate", generate_answer)

    # Define the flow
    workflow.set_entry_point("search")
    workflow.add_edge("search", "generate")
    workflow.add_edge("generate", END)

    return workflow.compile()


# Chainlit event handlers
@cl.on_chat_start
async def start():
    """
    Called when a new chat session starts
    """
    logger.info("🚀 New chat session started")

    # Store the agent graph in session
    agent = create_agent_graph()
    cl.user_session.set("agent", agent)
    logger.info("✅ Agent graph created and stored in session")

    await cl.Message(
        content="👋 **Welcome to ProductIQ AI Assistant!**\n\n"
                "I can help you find products from our catalog of 1,000 items.\n\n"
                "**Try asking:**\n"
                "- What wireless headphones do you have?\n"
                "- Show me running shoes\n"
                "- I need a laptop for gaming\n"
                "- What's the best coffee maker?\n\n"
                "Go ahead, ask me anything!"
    ).send()


@cl.on_message
async def main(message: cl.Message):
    """
    Called when user sends a message
    """
    logger.info(f"💬 User message: {message.content}")

    agent = cl.user_session.get("agent")

    thinking_msg = cl.Message(content="🔍 Searching products...")
    await thinking_msg.send()

    try:
        # Initial state
        initial_state = {
            "query": message.content,
            "search_results": [],
            "answer": "",
            "error": None
        }

        logger.info("🔄 Executing LangGraph agent...")
        result = await agent.ainvoke(initial_state)
        logger.info("✅ Agent execution completed")

        await thinking_msg.remove()

        # Show search results as a step
        if result["search_results"]:
            results_text = f"**Found {len(result['search_results'])} relevant products**\n\n"
            for i, product in enumerate(result["search_results"], 1):
                results_text += f"{i}. {product['title']} (Score: {product['score']:.2f})\n"

            await cl.Message(
                content=results_text,
                author="Search Engine"
            ).send()
            logger.info(f"📊 Displayed {len(result['search_results'])} search results")

        await cl.Message(
            content=result["answer"],
            author="AI Assistant"
        ).send()
        logger.info("📤 Sent AI response to user")

    except Exception as e:
        logger.error(f"❌ Error in agent execution: {str(e)}")
        await thinking_msg.remove()
        await cl.Message(
            content=f"❌ An error occurred: {str(e)}\n\n"
                    "Please make sure:\n"
                    "1. FastAPI server is running (http://localhost:8000)\n"
                    "2. GROQ_API_KEY is set in your environment"
        ).send()


if __name__ == "__main__":
    print("Agent started..")

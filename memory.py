"""
memory.py — Tobby's Long-Term Memory Core + Memory Agent
------------------------------------------------------------
Handles episodic memory (raw history) and reflective memory
(distilled lessons), using ChromaDB for storage and Gemini
embeddings for semantic search.

The Memory Agent (process_and_remember) reasons about what's
worth storing, rather than blindly saving everything.
"""

import os
import json
import time
import chromadb
import google.generativeai as genai
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")
genai.configure(api_key=GEMINI_API_KEY)

# ---------------------------------------------------------
# ChromaDB setup — persistent storage on disk
# ---------------------------------------------------------
chroma_client = chromadb.PersistentClient(path="./tobby_memory")

episodic_memory = chroma_client.get_or_create_collection(name="episodic")
reflective_memory = chroma_client.get_or_create_collection(name="reflective")

# ---------------------------------------------------------
# Gemini generation model — used for the Memory Agent's reasoning
# ---------------------------------------------------------
model = genai.GenerativeModel(model_name="gemini-3.5-flash-lite")


def get_embedding(text: str):
    """Converts text into a vector using Gemini's embedding model."""
    result = genai.embed_content(
        model="models/gemini-embedding-001",
        content=text,
    )
    return result["embedding"]


def save_episodic_memory(text: str):
    """Stores a raw conversation snippet."""
    embedding = get_embedding(text)
    memory_id = f"ep_{datetime.now().timestamp()}"

    episodic_memory.add(
        ids=[memory_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"timestamp": str(datetime.now())}],
    )


def save_reflective_memory(text: str):
    """Stores a distilled lesson."""
    embedding = get_embedding(text)
    memory_id = f"ref_{datetime.now().timestamp()}"

    reflective_memory.add(
        ids=[memory_id],
        embeddings=[embedding],
        documents=[text],
        metadatas=[{"timestamp": str(datetime.now())}],
    )


def recall_relevant_memories(query: str, top_k: int = 3):
    """Searches both memory types for what's relevant to the query."""
    query_embedding = get_embedding(query)

    episodic_results = episodic_memory.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )
    reflective_results = reflective_memory.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    episodic_texts = episodic_results["documents"][0] if episodic_results["documents"] else [
    ]
    reflective_texts = reflective_results["documents"][0] if reflective_results["documents"] else [
    ]

    return {
        "episodic": episodic_texts,
        "reflective": reflective_texts,
    }


# ---------------------------------------------------------
# MEMORY AGENT — reasons about what to store, instead of
# blindly saving everything
# ---------------------------------------------------------

def decide_memory_action(new_text: str):
    """
    Asks Gemini to reason about what to do with a new piece of
    information, given what's already stored in memory.
    """
    existing = recall_relevant_memories(new_text, top_k=3)

    if existing["episodic"] or existing["reflective"]:
        existing_context = f"""
Existing episodic memories that might be related:
{existing["episodic"]}

Existing reflective memories that might be related:
{existing["reflective"]}
"""
    else:
        existing_context = "No related memories currently exist."

    prompt = f"""
You are Tobby's memory reasoning system. Decide what to do with this
new piece of information.

NEW INFORMATION:
"{new_text}"

{existing_context}

Decide the following and respond ONLY in this exact JSON format,
nothing else, no markdown, no explanation outside the JSON:

{{
  "worth_remembering": true or false,
  "memory_type": "episodic" or "reflective",
  "action": "store_new" or "duplicate_skip" or "update_existing",
  "reason": "one short sentence explaining the decision"
}}

Rules:
- "episodic" = a specific event or thing that happened once
- "reflective" = a lasting fact, preference, or lesson about Drissin
- If it's small talk, a greeting, or has no lasting value, worth_remembering = false
- If something very similar already exists and adds nothing new, action = "duplicate_skip"
- If it updates/corrects existing memory, action = "update_existing"
- Otherwise action = "store_new"
"""

    response = model.generate_content(prompt)
    raw = response.text.strip()
    raw = raw.replace("```json", "").replace("```", "").strip()

    try:
        decision = json.loads(raw)
        return decision
    except json.JSONDecodeError:
        return {
            "worth_remembering": False,
            "memory_type": "episodic",
            "action": "duplicate_skip",
            "reason": "Failed to parse decision, skipping to be safe",
        }


def process_and_remember(text: str):
    """
    The main Memory Agent entry point. Call this instead of
    save_episodic_memory/save_reflective_memory directly.
    """
    decision = decide_memory_action(text)

    if not decision.get("worth_remembering", False):
        print(f"[Memory Agent] Skipped: {decision.get('reason')}")
        return decision

    if decision.get("action") == "duplicate_skip":
        print(f"[Memory Agent] Duplicate, skipped: {decision.get('reason')}")
        return decision

    memory_type = decision.get("memory_type", "episodic")

    if memory_type == "reflective":
        save_reflective_memory(text)
    else:
        save_episodic_memory(text)

    print(f"[Memory Agent] Stored as {memory_type}: {decision.get('reason')}")
    return decision


# ---------------------------------------------------------
# Manual test block
# ---------------------------------------------------------
if __name__ == "__main__":
    print("Testing Memory Agent...\n")

    text = "I'm doing my BCA at Bharathiar University in AI/ML"
    print(f"\nInput: {text}")
    process_and_remember(text)

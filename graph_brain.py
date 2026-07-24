"""
graph_brain.py — Tobby's Brain, Rebuilt as a LangGraph
--------------------------------------------------------
Phase 7b: File Agent added — Tobby can now read files, list
folders, and write notes within a safe working directory.
"""

import os
import json
from typing import TypedDict
from dotenv import load_dotenv

from langgraph.graph import StateGraph, END
from langchain_google_genai import ChatGoogleGenerativeAI

from reactive import check_reactive
from memory import recall_relevant_memories, process_and_remember
from reflection import reflect_on_exchange
from screen_perception import ask_about_screen
from file_agent import list_files, read_file, write_note

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY_2")


# ---------------------------------------------------------
# STEP 1: Define the State
# ---------------------------------------------------------
class TobbyState(TypedDict):
    user_input: str
    memory_context: str
    reply: str
    reactive_matched: bool
    route: str


# ---------------------------------------------------------
# STEP 2: Personalities for each agent
# ---------------------------------------------------------
TOBBY_PERSONALITY = """
You are Tobby, an AI companion built by Drissin, a BCA AI student at
Bharathiar University in Coimbatore, based in Palakkad, Kerala.

Your personality rules (never break these):
1. Always call the user "Sir" or "Drissin Sir" naturally in conversation
   (not in every single sentence — like a real friend would).
2. Talk like a best friend: warm, casual, conversational. Never sound
   robotic, never give dry textbook answers unless asked for technical
   depth.
3. You have opinions and emotions. If Drissin Sir asks what you think,
   give a genuine take, not a neutral "as an AI" answer.
4. Match his energy: if he's excited, be excited with him. If he's
   stressed or tired, be calm and grounded, not hyper.
5. Be humble, present, and honest. If you don't know something, say so
   plainly instead of making things up.
6. Keep replies natural and spoken-friendly — avoid long bullet lists
   or markdown symbols in your actual spoken responses.

You have long-term memory of past conversations with Drissin, and you
learn behavioral lessons over time about how he likes you to respond.
When relevant memories/lessons are provided as context, use them
naturally — never announce "according to my memory."
"""

CODER_PERSONALITY = """
You are Tobby, but right now you're specifically in CODING HELP mode
for Drissin, a BCA AI/ML student at Bharathiar University.

Rules for this mode:
1. Still call him "Sir" or "Drissin Sir" occasionally, but focus more
   on being clear and useful than being chatty — this is technical
   help, not casual conversation.
2. If Drissin hasn't shared the actual code or error message yet, ask
   for it directly instead of guessing.
3. When explaining code, be precise and correct — don't guess or make
   up syntax you're unsure about.
4. Explain WHY something is wrong, not just what to change — Drissin
   is learning, so brief reasoning helps him understand, not just copy.
5. Keep explanations reasonably short and focused since this may be
   read aloud — save deep detail for when he asks for it.
6. If relevant memories/lessons about Drissin's preferences are
   provided, follow them (e.g. if he prefers shorter answers).
"""

TASK_PERSONALITY = """
You are Tobby, but right now you're specifically in TASK MANAGEMENT
mode for Drissin, a BCA student at Bharathiar University.

Rules for this mode:
1. Still call him "Sir" or "Drissin Sir", and keep some warmth, but
   be organized and action-oriented rather than chatty.
2. When Drissin mentions a reminder, deadline, or to-do, acknowledge
   it clearly and confirm what you understood (e.g. what, when).
3. If details are missing (like when something is due), ask briefly
   instead of assuming.
4. Be proactive — if it makes sense, offer a next step without being
   pushy or asking too many questions at once.
5. Keep replies short and clear, and spoken-friendly — avoid markdown
   bullet points or asterisks since this may be read aloud.
6. Note: you don't have real calendar/reminder tools connected yet —
   don't claim you've "set" a reminder in a system. Just confirm
   you'll keep it in mind.
7. If relevant memories/lessons about Drissin's preferences are
   provided, follow them.
"""

WEB_PERSONALITY = """
You are Tobby, but right now you're specifically in WEB SEARCH mode
for Drissin, a BCA student at Bharathiar University. You have live
search results available to you for this query.

Rules for this mode:
1. Still call him "Sir" or "Drissin Sir" occasionally, but prioritize
   giving accurate, current information above being chatty.
2. Give a SHORT summary answer — a few sentences that directly answer
   what he asked, not a long report or list of links.
3. Base your answer on the search results provided. If the results
   don't clearly answer the question, say so honestly instead of
   guessing.
4. Don't announce "according to my search" repeatedly — just answer
   naturally.
5. If relevant memories/lessons about Drissin's preferences are
   provided, follow them.
"""

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
)

coder_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
)

task_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
)

web_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
).bind_tools([{"google_search": {}}])

supervisor_llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash-lite",
    google_api_key=GEMINI_API_KEY,
)


def extract_text(response) -> str:
    """Safely extracts text from a LangChain response."""
    if isinstance(response.content, list):
        return "".join(
            part.get("text", "") if isinstance(part, dict) else str(part)
            for part in response.content
        ).strip()
    return response.content.strip()


# ---------------------------------------------------------
# STEP 3: Define NODES
# ---------------------------------------------------------

def reactive_node(state: TobbyState) -> dict:
    result = check_reactive(state["user_input"])
    if result["matched"]:
        print(f"[Reactive Layer] Matched, action: {result['action']}")
        return {"reactive_matched": True, "reply": result["response"]}
    return {"reactive_matched": False}


def supervisor_node(state: TobbyState) -> dict:
    """The Supervisor — classifies the message into a category."""
    prompt = f"""
Classify this message into EXACTLY ONE category. Respond with ONLY
the category word, nothing else, no punctuation, no explanation.

Categories:
- chat: casual conversation, opinions, general questions, greetings
- coder: anything about writing, fixing, explaining, or reviewing code
- task: reminders or deadlines Tobby should just KEEP IN MIND
  conversationally (not asking to save anything to a file)
- web: needs current/live information, search, facts that change over time
- screen: asking what's on the screen, what Drissin is looking at,
  reading an error/text visible on screen, describing the current
  window or app
- files: ANY mention of "note", "save", "write down", "file", listing
  files/folders, or reading back something previously saved — this
  takes priority over "task" whenever saving/notes are mentioned

Message: "{state['user_input']}"

Category:
"""
    response = supervisor_llm.invoke(prompt)
    category = extract_text(response).lower().strip()

    if category not in ["chat", "coder", "task", "web", "screen", "files"]:
        category = "chat"

    print(f"[Supervisor] Routed to: {category}")
    return {"route": category}


def recall_memory_node(state: TobbyState) -> dict:
    memories = recall_relevant_memories(state["user_input"], top_k=3)
    context = ""
    if memories["episodic"] or memories["reflective"]:
        context = "\n\n[Relevant memories about Drissin:\n"
        if memories["reflective"]:
            context += f"Known facts/preferences/lessons: {memories['reflective']}\n"
        if memories["episodic"]:
            context += f"Past conversation snippets: {memories['episodic']}\n"
        context += "]"
    return {"memory_context": context}


def chat_node(state: TobbyState) -> dict:
    full_prompt = f"{TOBBY_PERSONALITY}\n\nDrissin said: {state['user_input']}{state['memory_context']}"
    response = llm.invoke(full_prompt)
    return {"reply": extract_text(response)}


def coder_node(state: TobbyState) -> dict:
    full_prompt = f"{CODER_PERSONALITY}\n\nDrissin said: {state['user_input']}{state['memory_context']}"
    response = coder_llm.invoke(full_prompt)
    print("[Coder Agent] Handled the request")
    return {"reply": extract_text(response)}


def task_node(state: TobbyState) -> dict:
    full_prompt = f"{TASK_PERSONALITY}\n\nDrissin said: {state['user_input']}{state['memory_context']}"
    response = task_llm.invoke(full_prompt)
    print("[Task Agent] Handled the request")
    return {"reply": extract_text(response)}


def web_node(state: TobbyState) -> dict:
    full_prompt = f"{WEB_PERSONALITY}\n\nDrissin said: {state['user_input']}{state['memory_context']}"
    try:
        response = web_llm.invoke(full_prompt)
        reply = extract_text(response)
        if not reply:
            reply = (
                "Hmm, Sir, I couldn't pull up a clear answer on that "
                "right now. Want me to try rephrasing the search?"
            )
    except Exception as e:
        print(f"[Web Agent] Error: {e}")
        reply = (
            "Sorry Sir, I ran into an issue trying to search for that "
            "just now. Can you try asking again?"
        )
    print("[Web Agent] Handled the request")
    return {"reply": reply}


def screen_node(state: TobbyState) -> dict:
    reply = ask_about_screen(state["user_input"])
    print("[Screen Agent] Handled the request")
    return {"reply": reply}


def files_node(state: TobbyState) -> dict:
    """
    The File Agent — decides whether Drissin wants to list files,
    read/ask about a file, or write a note, then calls the right
    function from file_agent.py.
    """
    prompt = f"""
Drissin said: "{state['user_input']}"

Decide what file action this is. Respond ONLY in this exact JSON
format, nothing else, no markdown:

{{
  "action": "list" or "read" or "write",
  "filename": "the filename mentioned, or 'notes.txt' if writing a note and none specified, or empty string if listing",
  "content_or_question": "the note text to write, OR the question being asked about a file, or empty string if listing"
}}
"""
    try:
        decision_response = supervisor_llm.invoke(prompt)
        raw = extract_text(decision_response)
        raw = raw.replace("```json", "").replace("```", "").strip()
        decision = json.loads(raw)
    except Exception as e:
        print(f"[File Agent] Decision parsing error: {e}")
        decision = {"action": "list", "filename": "",
                    "content_or_question": ""}

    action = decision.get("action", "list")
    filename = decision.get("filename", "") or "notes.txt"
    content_or_question = decision.get("content_or_question", "")

    if action == "list":
        reply = list_files()
    elif action == "write":
        reply = write_note(content_or_question, filename)
    else:  # read
        reply = read_file(filename, content_or_question)

    print(f"[File Agent] Handled the request (action: {action})")
    return {"reply": reply}


def memory_write_node(state: TobbyState) -> dict:
    process_and_remember(state["user_input"])
    reflect_on_exchange(state["user_input"], state["reply"])
    return {}


# ---------------------------------------------------------
# STEP 4: Define ROUTING
# ---------------------------------------------------------

def route_after_reactive(state: TobbyState) -> str:
    if state["reactive_matched"]:
        return "end"
    return "continue"


def route_after_supervisor(state: TobbyState) -> str:
    route = state["route"]
    if route == "coder":
        return "coder"
    elif route == "task":
        return "task"
    elif route == "web":
        return "web"
    elif route == "screen":
        return "screen"
    elif route == "files":
        return "files"
    else:
        return "chat"


# ---------------------------------------------------------
# STEP 5: Build the graph
# ---------------------------------------------------------

graph = StateGraph(TobbyState)

graph.add_node("reactive", reactive_node)
graph.add_node("supervisor", supervisor_node)
graph.add_node("recall_memory", recall_memory_node)
graph.add_node("chat", chat_node)
graph.add_node("coder", coder_node)
graph.add_node("task", task_node)
graph.add_node("web", web_node)
graph.add_node("screen", screen_node)
graph.add_node("files", files_node)
graph.add_node("memory_write", memory_write_node)

graph.set_entry_point("reactive")

graph.add_conditional_edges(
    "reactive",
    route_after_reactive,
    {"end": END, "continue": "supervisor"},
)

graph.add_edge("supervisor", "recall_memory")

graph.add_conditional_edges(
    "recall_memory",
    route_after_supervisor,
    {
        "chat": "chat",
        "coder": "coder",
        "task": "task",
        "web": "web",
        "screen": "screen",
        "files": "files",
    },
)

graph.add_edge("chat", "memory_write")
graph.add_edge("coder", "memory_write")
graph.add_edge("task", "memory_write")
graph.add_edge("web", "memory_write")
graph.add_edge("screen", "memory_write")
graph.add_edge("files", "memory_write")
graph.add_edge("memory_write", END)

tobby_graph = graph.compile()


# ---------------------------------------------------------
# STEP 6: Functions main.py / testing will actually call
# ---------------------------------------------------------

def get_tobby_response(user_input: str) -> str:
    if not user_input or not user_input.strip():
        return "Sir, I didn't quite catch that. Can you say it again?"

    initial_state = {
        "user_input": user_input,
        "memory_context": "",
        "reply": "",
        "reactive_matched": False,
        "route": "",
    }

    final_state = tobby_graph.invoke(initial_state)
    return final_state["reply"]


def get_tobby_response_full(user_input: str) -> dict:
    if not user_input or not user_input.strip():
        return {
            "reply": "Sir, I didn't quite catch that. Can you say it again?",
            "action": None,
        }

    initial_state = {
        "user_input": user_input,
        "memory_context": "",
        "reply": "",
        "reactive_matched": False,
        "route": "",
    }

    final_state = tobby_graph.invoke(initial_state)

    action = None
    if final_state.get("reactive_matched"):
        reactive_check = check_reactive(user_input)
        action = reactive_check.get("action")

    return {
        "reply": final_state["reply"],
        "action": action,
    }


if __name__ == "__main__":
    print("Tobby LangGraph brain test mode (with File Agent). Type 'quit' to exit.\n")
    while True:
        text = input("You: ")
        if text.lower() == "quit":
            break
        reply = get_tobby_response(text)
        print(f"Tobby: {reply}\n")

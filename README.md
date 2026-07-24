# Tobby 2.0 — Personal Agentic AI Companion

Tobby is a voice-first personal AI assistant built from scratch as a learning project while pursuing a BCA in AI at Bharathiar University. It started as a simple wake-word voice assistant and evolved into a full agentic AI system with long-term memory, behavioral learning, and multiple specialized agents working together.

## What Tobby Can Do

- **Wake word activation** — whistle to wake Tobby up, no button presses needed
- **Natural voice conversation** — speech-to-text (Whisper) in, natural TTS voice out, with interruption handling so you can cut Tobby off mid-sentence
- **Long-term memory** — remembers facts and past conversations across sessions using a vector database, not just within a single chat
- **Behavioral learning** — reflects on conversations to learn *how* you like to be talked to (shorter answers, humor, tone), not just *what* you told it
- **Multi-agent routing** — a supervisor agent classifies each request and routes it to the right specialist:
  - **Chat Agent** — casual conversation
  - **Coder Agent** — focused technical help, asks for missing context, explains reasoning
  - **Task Agent** — reminders and planning
  - **Web Agent** — live web search with search grounding for current information
  - **Screen Agent** — takes a screenshot and answers questions about what's on your screen
  - **Files Agent** — reads, lists, and writes local notes/files in a safe sandboxed folder
- **Reactive fast-path** — simple commands like "stop" or "go to sleep" skip the full AI pipeline for instant response

## Architecture

Built on **LangGraph**, using a state graph rather than simple sequential function calls:
reactive → supervisor → memory recall → specialist agent → memory write → reflection
- **Memory system**: ChromaDB with Gemini embeddings, split into episodic memory (raw events) and reflective memory (distilled behavioral lessons)
- **LLM**: Google Gemini (`gemini-3.5-flash-lite`) for all reasoning, chat, and vision tasks
- **Voice**: `SpeechRecognition` + Whisper for input, `edge-tts` for output
- **Screen perception**: `mss` for screenshot capture, sent directly to Gemini's multimodal input

## Tech Stack

Python, LangGraph, ChromaDB, Google Gemini API, Flask, edge-tts, Whisper (faster-whisper), Electron (HUD, in progress)

## Status

Actively in development. Core agentic brain, memory, reflection, and voice pipeline are fully working. Currently exploring a desktop HUD interface and RAG-based document search as next steps.

## Why I Built This

I wanted to go beyond tutorial-level chatbots and actually understand how production agentic systems are designed — memory architecture, hierarchical agent routing, context engineering, and the reflection/reactive/tool-use patterns used in real AI systems. This project has been my hands-on way of learning that by building it end to end.

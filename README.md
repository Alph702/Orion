# ORION — Omnipresent Responsive Intelligent Operations Network (Preview)

> ⚠️ This is the **first functional module** of ORION — a broader intelligent assistant system. What you're reading is documentation for just **one puzzle piece** in development, not the complete ORION project.

---

## 🌟 Welcome to ORION

**ORION (Omnipresent Responsive Intelligent Operations Network)** is a modular, intelligent assistant framework designed to understand user intent and route commands to specialized modules — such as AI reasoning, weather APIs, music control, or system automation.

This document introduces the **first stage** of the system — the **Routing Module**, which translates raw human input into structured module commands.

🔧 Built with extensibility in mind, ORION will eventually combine:

* Natural language understanding
* Modular action routing
* Smart home, study, and productivity integrations
* Voice interface and memory context

You are currently looking at the routing core that makes this possible. As development progresses, more modules will integrate into this ecosystem.

---

## 📁 Project Structure

```
Orion/
├── Backend/
│   ├── model.py          # Core logic for processing user input
│   ├── RealtimeData.py   # Real-time info (weather, search, etc.)
│   ├── STT.py            # Speech-to-text (FastNaturalSpeechRecognition)
│   └── TTS.py            # Text-to-speech (OrionTTS)
├── Brain/
│   ├── model.py          # OrionModel: main assistant logic
│   └── Data/
│       ├── ChatHistory.json   # Conversation history
│       ├── orionconfig.json   # User/config data
│       ├── TTS_runing.orion   # TTS running state
│       ├── TTS_stop.orion     # TTS stop state
│       └── stop.orion         # Assistant stop state
├── tests/
│   ├── test_model.py          # Test cases for the model
│   ├── test_summary_length.py # Test for summary length
│   └── test_min_summary_length.py # Test for min summary length
├── main.py               # Entry point for the application
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # Project documentation
```

---

## 🎯 Purpose of This Module

This routing module:

* Accepts **natural user input** (spoken or typed)
* Strips irrelevant filler words
* Decomposes complex instructions into clean, actionable module calls
* Returns a **Python list of \['MODULE', 'QUERY']** pairs, ready to be dispatched

---

## 🧠 Core Components

- **OrionModel**: Main assistant logic (function-calling, context-aware, routes to modules)
- **Chatbot**: Handles general queries, context-based responses
- **RealtimeData**: Fetches real-time info (weather, time, search, etc.)
- **FastNaturalSpeechRecognition**: Speech-to-text engine
- **OrionTTS**: Text-to-speech engine (supports multiple backends)

---

## 🛠️ Function Calling & Tools

- **Chatbot**: For general, weather, time, location, and search queries. Uses context tags.
- **Search**: Explicit web search (with `query`, `max_results`, `min_summary_length`).
- **Stop**: Halts assistant operations (e.g., "stop listening", "exit", "mute").

---

## 🗂️ Data & State Files

- `ChatHistory.json`: Stores all user/assistant conversations.
- `orionconfig.json`: User and configuration data.
- `TTS_runing.orion`, `TTS_stop.orion`, `stop.orion`: Track TTS and assistant running/stopped state.

---

## 🧪 Testing

- `tests/test_model.py`: Model logic tests.
- `tests/test_summary_length.py`, `tests/test_min_summary_length.py`: Validate summary extraction logic.

---

## 🚦 Example Usage

- **General Query**: "What's the weather and time in Karachi?"
- **Search**: "Search for latest AI news"
- **Stop**: "Stop listening", "exit", "mute"

The assistant will route these to the appropriate function/tool and return structured results.

---

## 🚀 Roadmap

- Add more modules (music, smart home, productivity, etc.)
- Enhance memory/context handling
- Improve voice and multimodal support
- Expand API integrations

---

## 📝 Contributing

Contributions are welcome! Please open issues or pull requests for improvements, bug fixes, or new modules.

---

## 📄 License

MIT License

---

**This is only the beginning.** ORION will grow into a full assistant system that thinks, remembers, and acts across domains.

Stay tuned! 🌌

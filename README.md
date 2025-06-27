# ORION — Omnipresent Responsive Intelligent Operations Network (Preview)

> ⚠️ This is the **first functional module** of ORION — a broader intelligent assistant system. What you're reading is documentation for just **one puzzle piece** in development, not the complete ORION project.

---

## 🌟 Welcome to ORION

**ORION (Omnipresent Responsive Intelligent Operations Network)** is a modular, intelligent assistant framework designed to understand user intent and route commands to specialized modules — such as AI reasoning, weather APIs, music control, or system automation.

This document introduces the **first stage** of the system — the **Routing Module**, which translates raw human input into structured module commands.

---

## 🚀 Latest Features

- **Real-Time Web Data**: Fetches live weather, time, and search results using external APIs.
- **Modular Skills**: Supports music, smart home, study tools, and system commands.
- **User Identity Awareness**: Remembers and addresses the user by name (e.g., Amanat Ali).
- **Conversational Memory**: Maintains context for more natural, multi-turn conversations.
- **Error Handling**: Gracefully manages rate limits, missing data, and unclear queries.
- **Flexible Input**: Accepts both voice and text, with robust fallback and clarification prompts.
- **Extensible Design**: Easily add new modules for custom skills and integrations.

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
=======
│   ├── RealtimeData.py       # Real-time data fetching and processing
│   ├── STT.py                # Speech-to-text engine integrations
│   └── TTS.py                # Text-to-speech engine integrations
├── Brain/
│   ├── ChatBot.py            # Main chatbot logic and conversation management
│   ├── model.py              # Core logic for intent routing and module selection
│   └── Data/
│       ├── ChatHistory.json  # Conversation history and context
│       └── orionconfig.json  # User and system configuration
├── .env                      # Environment variables
├── .gitignore                # Git ignore file
├── main.py                   # Entry point for the application
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## 🎯 Purpose of This Module

This routing module:

* Accepts **natural user input** (spoken or typed)
* Strips irrelevant filler words
* Decomposes complex instructions into clean, actionable module calls
* Returns a **Python list of ['MODULE', 'QUERY']** pairs, ready to be dispatched
* Integrates with real-time APIs for weather, time, and search
* Handles user identity and context for personalized responses

---

## 🧩 Supported Modules

- `WEATHER` — Weather questions (e.g., rain, temperature)
- `LOCATION` — Location questions (e.g., "Where am I?")
- `TIME` — Time or date questions
- `SEARCH` — Real-world facts, people, events, info
- `SYSTEM_COMMANDS` — OS/app actions (e.g., open Notion)
- `CUSTOM_SKILL_MUSIC` — Music playback/control
- `CUSTOM_SKILL_HOME` — Smart home commands (lights, fan)
- `CUSTOM_SKILL_STUDY` — Study tools, Notion, Anki, tasks
- `CHATBOT` — General conversation, fallback, and clarification

---

## 🧠 Assistant Capabilities

- Answers questions clearly and briefly, like a human assistant
- Understands and responds to voice and text
- Asks the user to repeat if input is unclear
- Handles knowledge, conversations, summaries, and smart responses
- Works with real-time web data if available (like weather, news, etc.)
- Respects and follows the personality and purpose given by the user

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

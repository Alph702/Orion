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

🚀 **This is only the beginning.** ORION will grow into a full assistant system that thinks, remembers, and acts across domains.

Stay tuned! 🌌

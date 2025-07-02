```md
// filepath: d:\Code\Orion\README.md
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

│   ├── test_summary_length.py # Test for summary length
│   └── test_min_summary_length.py # Test for min summary length
├── main.py               # Entry point for the application
├── requirements.txt      # Python dependencies
├── .gitignore            # Git ignore file
└── README.md             # Project documentation

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

// ...existing code...

## 🧠 Core Components

// ...existing code...

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
```

```js
// filepath: d:\Code\Orion\Frontend\eslint.config.js
import js from '@eslint/js'
import globals from 'globals'
import reactHooks from 'eslint-plugin-react-hooks'
import reactRefresh from 'eslint-plugin-react-refresh'
import { defineConfig, globalIgnores } from 'eslint/config'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{js,jsx}'],
    extends: [
      js.configs.recommended,
      reactHooks.configs['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      ecmaVersion: 2020,
      globals: globals.browser,
      parserOptions: {
        ecmaVersion: 'latest',
        ecmaFeatures: { jsx: true },
        sourceType: 'module',
      },
    },
    rules: {
      'no-unused-vars': ['error', { varsIgnorePattern: '^[A-Z_]' }],
    },
  },
])
```

```json
// filepath: d:\Code\Orion\Frontend\package.json
{
  "name": "orion-ui",
  "private": true,
  "version": "0.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "vite build",
    "lint": "eslint .",
    "preview": "vite preview"
  },
  "dependencies": {
    "react": "^19.1.0",
    "react-dom": "^19.1.0"
  },
  "devDependencies": {
    "@eslint/js": "^9.29.0",
    "@types/react": "^19.1.8",
    "@types/react-dom": "^19.1.6",
    "@vitejs/plugin-react": "^4.5.2",
    "eslint": "^9.29.0",
    "eslint-plugin-react-hooks": "^5.2.0",
    "eslint-plugin-react-refresh": "^0.4.20",
    "globals": "^16.2.0",
    "vite": "^7.0.0"
  }
}
```

```js
// filepath: d:\Code\Orion\Frontend\vite.config.js
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  server: {
    proxy: {
      '/api': 'http://localhost:5000'
    }
  }
})
```

```
// filepath: d:\Code\Orion\Frontend\.gitignore
# Logs
logs
*.log
npm-debug.log*
yarn-debug.log*
yarn-error.log*
pnpm-debug.log*
lerna-debug.log*

node_modules
dist
dist-ssr
*.local

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
.DS_Store
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
```

```html
<!-- filepath: d:\Code\Orion\Frontend\index.html -->
<!doctype html>
<html lang="en">
  <head>
    <meta charset="UTF-8" />
    <link rel="icon" type="image/svg+xml" href="/vite.svg" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>Vite + React</title>
  </head>
  <body>
    <div id="root"></div>
    <script type="module" src="/src/main.jsx"></script>
  </body>
</html>
```

```css
/* filepath: d:\Code\Orion\Frontend\src\App.css */
#root {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem;
  text-align: center;
}

.logo {
  height: 6em;
  padding: 1.5em;
  will-change: filter;
  transition: filter 300ms;
}
.logo:hover {
  filter: drop-shadow(0 0 2em #646cffaa);
}
.logo.react:hover {
  filter: drop-shadow(0 0 2em #61dafbaa);
}

@keyframes logo-spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

@media (prefers-reduced-motion: no-preference) {
  a:nth-of-type(2) .logo {
    animation: logo-spin infinite 20s linear;
  }
}

.card {
  padding: 2em;
}

.read-the-docs {
  color: #888;
}
```

```css
/* filepath: d:\Code\Orion\Frontend\src\index.css */
:root {
  font-family: system-ui, Avenir, Helvetica, Arial, sans-serif;
  line-height: 1.5;
  font-weight: 400;

  color-scheme: light dark;
  color: rgba(255, 255, 255, 0.87);
  background-color: #242424;

  font-synthesis: none;
  text-rendering: optimizeLegibility;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  font-weight: 500;
  color: #646cff;
  text-decoration: inherit;
}
a:hover {
  color: #535bf2;
}

body {
  margin: 0;
  display: flex;
  place-items: center;
  min-width: 320px;
  min-height: 100vh;
}

h1 {
  font-size: 3.2em;
  line-height: 1.1;
}

button {
  border-radius: 8px;
  border: 1px solid transparent;
  padding: 0.6em 1.2em;
  font-size: 1em;
  font-weight: 500;
  font-family: inherit;
  background-color: #1a1a1a;
  cursor: pointer;
  transition: border-color 0.25s;
}
button:hover {
  border-color: #646cff;
}
button:focus,
button:focus-visible {
  outline: 4px auto -webkit-focus-ring-color;
}

@media (prefers-color-scheme: light) {
  :root {
    color: #213547;
    background-color: #ffffff;
  }
  a:hover {
    color: #747bff;
  }
  button {
    background-color: #f9f9f9;
  }
}
```

```jsx
// filepath: d:\Code\Orion\Frontend\src\App.jsx
import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  return (
    <>
      <div>
        <a href="https://vite.dev" target="_blank">
          <img src={viteLogo} className="logo" alt="Vite logo" />
        </a>
        <a href="https://react.dev" target="_blank">
          <img src={reactLogo} className="logo react" alt="React logo" />
        </a>
      </div>
      <h1>Vite + React</h1>
      <div className="card">
        <button onClick={() => setCount((count) => count + 1)}>
          count is {count}
        </button>
        <p>
          Edit <code>src/App.jsx</code> and save to test HMR
        </p>
      </div>
      <p className="read-the-docs">
        Click on the Vite and React logos to learn more
      </p>
    </>
  )
}

export default App
```

```jsx
// filepath: d:\Code\Orion\Frontend\src\main.jsx
import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import './index.css'
import App from './App.jsx'
import MapWidget from './widgets/map.jsx'

createRoot(document.getElementById('root')).render(
  <StrictMode>
    <App />
    <MapWidget />
  </StrictMode>,
)
```

```jsx
// filepath: d:\Code\Orion\Frontend\src\widgets\map.jsx
// ...existing code...
```

```orion
// filepath: d:\Code\Orion\Brain\Data\TTS_runing.orion
true
```

```orion
// filepath: d:\Code\Orion\Brain\Data\TTS_stop.orion
false
```

```orion
// filepath: d:\Code\Orion\Brain\Data\stop.orion
True
```

```css
/* filepath: d:\Code\Orion\Backend\map\static\css\style.css */
body {
    font-family: sans-serif;
    margin: 0;
    padding: 20px;
    background: #f4f4f4;
    display: flex;
    flex-direction: column;
    min-height: 100vh;
}

#map-container {
    display: flex;
    flex-direction: column;
    flex-grow: 1;
}

#map {
    flex-grow: 1;
    min-height: 500px;
    border: 2px solid #444;
    border-radius: 8px;
    margin-top: 10px;
}

.form-container {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    margin-bottom: 20px;
}

.locations-container {
    display: flex;
    gap: 20px;
    flex-wrap: wrap;
}

.locations-list, .routes-list {
    background: white;
    padding: 15px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    flex-grow: 1;
    min-width: 300px;
}

ul {
    padding-left: 20px;
}

button {
    background: #3388ff;
    color: white;
    border: none;
    padding: 8px 15px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

button:hover {
    background: #2a7ae9;
}
```

```py
# filepath: d:\Code\Orion\Backend\RealtimeData.py
# ...existing code...
class RealTimeInformation:
    # ...existing code...
    def interpret_weather_code(self, code):
        code_map = {
            0: "Clear sky", 1: "Mainly clear", 2: "Partly cloudy", 3: "Overcast", 45: "Fog",
            48: "Rime fog", 51: "Light drizzle", 53: "Moderate drizzle", 55: "Heavy drizzle",
            61: "Slight rain", 63: "Moderate rain", 65: "Heavy rain", 71: "Light snow",
            73: "Moderate snow", 75: "Heavy snow", 80: "Rain showers", 81: "Heavy showers",
            82: "Violent rain", 95: "Thunderstorm", 96: "Storm with hail", 99: "Violent storm with hail"
        }
        return code_map.get(code, "Unknown condition")
    # ...existing code...
```

<!-- Add more files here as needed, following the same pattern. -->

# NOVA: Modular Voice-Based AI Assistant

> Intelligent desktop assistant built for **offline-first, modular, and personalized use**, featuring voice activation, dynamic skill execution, persistent memory, and future-ready NLP.

---

## 🧠 Overview

NOVA is a modular, voice-based desktop assistant designed to be responsive, customizable, and privacy-respecting. It supports wake-word activation, modular skills, local memory-based personalization, and context-aware interactions. Built with PyQt5 and Python 3, NOVA is designed for desktop environments without requiring persistent cloud connectivity.

---

## 📁 Project Structure

```bash
NOVA/
├── main.py                 # Launches GUI and core modules
├── core/                   # All critical system modules
│   ├── wake_word.py        # Wake-word detection (Porcupine/Google)
│   ├── stt.py              # Speech-to-text (Whisper/Google)
│   ├── nlp.py              # Intent recognition (Spacy + Rules)
│   ├── skill_manager.py    # Skill discovery and execution
│   ├── memory_manager.py   # Persistent user context (ChromaDB)
│   ├── mood.py             # Mood/emotion detection (WIP)
│   ├── tts.py              # Text-to-speech (pyttsx3)
├── features/               # User-defined skill scripts (Legacy support)
├── config/                 # API keys, constants
├── utils/images/           # Loading GIFs for UI
└── tests/                  # Unit tests for core logic
```

---

## 🔧 Installation

### Prerequisites:
- Python 3.9+ (Python 3.11 recommended for full compatibility)
- FFmpeg (for Whisper STT)
- Virtualenv (optional but recommended)

### Dependencies

```bash
pip install -r requirements.txt
```

**External Requirements:**
- `pvporcupine` for hotword detection (Requires AccessKey)
- `ffmpeg` for Whisper
- API keys if you plan to use web-based skills (e.g., Google Calendar)

---

## 🚀 How to Run

1. **Activate Environment** (if using `fix_env.sh`):
   ```bash
   source venv/bin/activate
   ```
2. **Run Main**:
   ```bash
   python main.py
   ```

**Once the GUI loads:**
1. Wait for it to initialize (Status: "Listening for 'Hey NOVA'...")
2. Speak the wake word: **"Porcupine"** (Default) or **"Hey NOVA"**
3. Ask a command like:
   - "What is the time?"
   - "Play lo-fi on YouTube"
   - "What's the weather in Dallas?"

---

## 🧩 Core Functionalities

### ✅ 1. Wake Word Activation (`core/wake_word.py`)
- Passive listener for the phrase “Hey NOVA” / "Porcupine".
- Runs in background thread (`WakeWordListener`).
- **Engine**: Porcupine (High Accuracy).

### ✅ 2. Speech-to-Text (`core/stt.py`)
- Converts audio to text using **Whisper** (Local, default) or Google STT (fallback).
- Emits transcribed text to NLP module via event signal.

### ✅ 3. Intent Recognition (`core/nlp.py`)
- Hybrid System:
  - **Spacy**: For Entity Recognition (extracting "Dallas" from "Weather in Dallas").
  - **Rules**: For critical commands ("time", "youtube").
- Future upgrade planned: DistilBERT / GPT prompt chaining.

### ✅ 4. Skill Manager (`core/skill_manager.py`)
- Dynamically loads and executes Python scripts from `features/`.
- **Note**: Some legacy skills need refactoring to return values instead of printing.

### ✅ 5. Memory Manager (`core/memory_manager.py`)
- **Engine**: **ChromaDB** (Vector Database).
- Stores: Past commands, Mood state, User preferences.
- Supports: Embedding lookup and contextual recall.

### ✅ 6. Mood Detection (`core/mood.py`)
- Placeholder logic for sentiment analysis via Tone in speech or Entity-based sentiment.
- Affects assistant response tone.

### ✅ 7. Text-to-Speech (`core/tts.py`)
- Converts system response into speech.
- **Backend**: `pyttsx3` (Offline).
- Executed on a separate thread to avoid blocking GUI.

### ✅ 8. GUI (`main.py` & `features/gui.py`)
- **Framework**: PyQt5.
- **Dashboard**:
  - Conversation history panel.
  - Live assistant status / voice interaction.
  - Skills tab + command builder.

---

## 🛠️ Skills (Features)

Located in `features/`. Each file corresponds to a user-executable "skill."

| File | Intent | Sample Query |
| :--- | :--- | :--- |
| `weather.py` | `get_weather` | "What's the weather today?" |
| `youtube_search.py` | `play_youtube` | "Play lo-fi hip hop on YouTube" |
| `google_calendar.py` | `check_calendar` | "What do I have tomorrow?" |
| `note.py` | `take_note` | "Take a note: buy protein" |
| `send_email.py` | `send_email` | "Send an email to Eric" |

> **⚠️ Note**: Legacy skill scripts currently print to stdout. Work is underway to refactor them to return strings for the GUI.

---

## 🧪 Testing

Unit tests are located in `tests/`.

To run:
```bash
python -m unittest discover tests
```

**Covers:**
- Intent parsing (`NLPHandler`)
- Basic skill routing (`SkillManager`)
- Memory storage/retrieval (`MemoryManager`)

---

## 📹 Phase 4 Deliverables (Required)

- ✅ **Communication Diagram** – Shows module interactions.
- ✅ **UI Code** – Located in `features/gui.py`.
- ✅ **Demo Recording** – Use `main.py` to demonstrate Wake Word + STT + Skill Execution.

---

## 🔮 Planned Features (Roadmap)

- [ ] **Refactor Skills**: Convert scripts to callable functions.
- [ ] **Plugin Loader**: Add/remove modules on the fly via GUI.
- [ ] **Web Dashboard**: Remote voice logs.
- [ ] **Mood Tracker**: Visual interface for detected sentiment.

---

## � Contributing

You can add new features by:
1. Creating a new `.py` in `/features`.
2. Registering its intent in `core/nlp.py`.
3. Updating `SkillManager` to route it.

---

## 🔐 Local-First & Privacy

- No audio data or logs are sent externally.
- Whisper STT runs locally.
- MemoryManager uses local vector DB (ChromaDB).
- Optional cloud APIs (e.g., Google Calendar) are opt-in only.

---

## 🧾 License

MIT — Built for educational and research purposes.

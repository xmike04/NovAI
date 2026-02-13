# nova
voice assistant project using python + pyqt5

## setup
install stuff:
pip install -r requirements.txt

create a .env file:
OPENAI_API_KEY=your_key_here

## running
python3 main.py

## structure
main.py - entry point
core/ - backend logic (stt, tts, llm)
features/ - skills (weather, profile, etc)
ui/ - gui code
config/ - user settings

## notes
- uses whisper for stt (local)
- uses openai for fallback
- wake word is 'jarvis'
- ui has 3 panels

## features
- voice commands
- weather, youtube, google
- remembers name and facts
- runs on macos

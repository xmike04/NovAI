import sys
import subprocess
import speech_recognition as sr
import pyttsx3

from NOVA.features import date_time
from NOVA.features import launch_app
from NOVA.features import website_open
from NOVA.features import weather
from NOVA.features import wikipedia
from NOVA.features.legacy import news
from NOVA.features import send_email
from NOVA.features import google_search
from NOVA.features.legacy import google_calendar
from NOVA.features import note
from NOVA.features.legacy import system_stats
from NOVA.features.legacy import loc


# =========================
# Text-to-Speech utilities
# =========================
def _init_tts():
    """
    Try to init pyttsx3 with a sensible driver for the OS.
    If it fails (e.g., PyObjC/objc import issues on macOS), return None
    so we can fall back to `say` on macOS.
    """
    if sys.platform.startswith("win"):
        candidates = ("sapi5", None)
    elif sys.platform == "darwin":
        candidates = ("nsss", None)
    else:
        candidates = ("espeak", None)

    for drv in candidates:
        try:
            eng = pyttsx3.init(drv)
            # Pick an English-ish voice if available
            voices = eng.getProperty("voices") or []
            voice_id = None
            for v in voices:
                name = (getattr(v, "name", "") or "").lower()
                lang = ",".join(getattr(v, "languages", [])).lower() if hasattr(v, "languages") else ""
                if "en" in name or "en" in lang:
                    voice_id = v.id
                    break
            if not voice_id and voices:
                voice_id = voices[0].id
            if voice_id:
                eng.setProperty("voice", voice_id)
            eng.setProperty("rate", 175)
            return eng
        except Exception as e:
            print(f"pyttsx3 init with driver {drv or 'default'} failed: {e}")
    return None


_ENGINE = _init_tts()


def speak(text: str) -> bool:
    """
    Speak text via pyttsx3 if available, otherwise fall back to macOS `say`.
    """
    if _ENGINE is not None:
        try:
            _ENGINE.say(text)
            _ENGINE.runAndWait()
            return True
        except Exception as e:
            print("pyttsx3 error, using 'say' fallback:", e)

    # Fallback (works on macOS)
    try:
        if sys.platform == "darwin":
            subprocess.run(["say", text])
            return True
    except Exception as e:
        print("Fallback 'say' failed:", e)
    return False


# =========================
# Assistant
# =========================
class NOVAAssistant:
    def __init__(self):
        pass

    # ---------- Speech input ----------
    def mic_input(self, *, device_index=None, timeout=5, phrase_time_limit=6, language="en-US"):
        """
        Listen once and return recognized text (lowercased). Returns "" on failure.
        - device_index: set to a specific mic index if needed
        - timeout: max seconds to wait for speech to start
        - phrase_time_limit: max seconds to capture once speaking
        - language: use "en-US" on macOS; change if you prefer
        """
        r = sr.Recognizer()
        r.dynamic_energy_threshold = True  # auto-adjusts to room noise

        try:
            with sr.Microphone(device_index=device_index) as source:
                print("Listening…")
                r.adjust_for_ambient_noise(source, duration=0.7)
                audio = r.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
        except sr.WaitTimeoutError:
            print("No speech detected (timeout).")
            return ""
        except Exception as e:
            print("Mic error:", e)
            return ""

        try:
            print("Recognizing…")
            text = r.recognize_google(audio, language=language)
            print("You said:", text)
            return text.lower()
        except sr.UnknownValueError:
            print("Sorry, I didn’t catch that.")
            return ""
        except sr.RequestError as e:
            print("Speech API error:", e)
            return ""

    # ---------- Speech output ----------
    def tts(self, text):
        """
        Convert any text to speech.
        """
        try:
            return speak(text)
        except Exception as e:
            print("TTS failed:", e)
            return False

    # ---------- Features ----------
    def tell_me_date(self):
        return date_time.date()

    def tell_time(self):
        return date_time.time()

    def launch_any_app(self, path_of_app):
        """
        Launch any Windows application.
        """
        return launch_app.launch_app(path_of_app)

    def website_opener(self, domain):
        """
        Open a website by domain (e.g., 'youtube.com').
        """
        return website_open.website_opener(domain)

    def weather(self, city):
        """
        Return weather info as string or False.
        """
        try:
            return weather.fetch_weather(city)
        except Exception as e:
            print(e)
            return False

    def tell_me(self, topic):
        """
        Summary from Wikipedia.
        """
        return wikipedia.tell_me_about(topic)

    def news(self):
        """
        Top news of the day.
        """
        return news.get_news()

    def send_mail(self, sender_email, sender_password, receiver_email, msg):
        return send_email.mail(sender_email, sender_password, receiver_email, msg)

    def google_calendar_events(self, text):
        try:
            service = google_calendar.authenticate_google()
            date = google_calendar.get_date(text)
            if date:
                return google_calendar.get_events(date, service)
        except FileNotFoundError:
            print("Google Calendar disabled: credentials.json not found.")
            self.tts("Google Calendar is not set up yet.")
            return []
        except Exception as e:
            print("Google Calendar error:", e)
            return []

    def search_anything_google(self, command):
        google_search.google_search(command)

    def take_note(self, text):
        note.note(text)

    def system_info(self):
        return system_stats.system_stats()

    def location(self, location):
        current_loc, target_loc, distance = loc.loc(location)
        return current_loc, target_loc, distance

    def my_location(self):
        city, state, country = loc.my_location()
        return city, state, country

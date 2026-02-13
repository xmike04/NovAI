import speech_recognition as sr
import whisper
import os
import tempfile
import openai
from dotenv import load_dotenv

load_dotenv()

class WhisperSTT:
    def __init__(self):
        print("Loading Whisper model (base)...")
        self.model = whisper.load_model("base")
        self.recognizer = sr.Recognizer()
        print("Whisper model loaded.")

    def transcribe(self, audio_source=None):
        """
        Transcribes audio to text using Whisper.
        Falls back to OpenAI API if available on error.
        """
        print("Listening/Transcribing...")
        temp_path = None
        
        try:
            with sr.Microphone() as source:
                # Fast adjust (0.5s) to avoid missing speech start
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                try:
                    # Enforce max duration to prevent infinite hanging
                    audio = self.recognizer.listen(source, timeout=5, phrase_time_limit=10)
                except sr.WaitTimeoutError:
                    return ""

            # Save to temp file
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav.write(audio.get_wav_data())
                temp_path = temp_wav.name
            
            # 1. Try Local Whisper
            try:
                result = self.model.transcribe(temp_path, fp16=False)
                text = result["text"].strip()
                if text:
                    return text
            except Exception as e:
                print(f"Local Whisper Error: {e}")
                
            # 2. Fallback to OpenAI API
            api_key = os.getenv("OPENAI_API_KEY")
            if api_key:
                print("Falling back to OpenAI Whisper API...")
                try:
                    client = openai.OpenAI(api_key=api_key)
                    with open(temp_path, "rb") as audio_file:
                        transcript = client.audio.transcriptions.create(
                            model="whisper-1", 
                            file=audio_file
                        )
                    return transcript.text.strip()
                except Exception as api_e:
                    print(f"OpenAI API Error: {api_e}")
            
            return ""

        except Exception as e:
            print(f"STT Critical Error: {e}")
            return ""
            
        finally:
            # Cleanup
            if temp_path and os.path.exists(temp_path):
                os.remove(temp_path)

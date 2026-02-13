import pyttsx3
import sys
import subprocess
from NOVA.core.config_manager import config_manager

class TTSModule:
    def __init__(self):
        self.engine = None 
        self.current_voice_id = config_manager.get("voice_id", "Victoria") 
        self.rate = config_manager.get("voice_speed", 200)
        self.process = None

        self._init_engine()

    def _init_engine(self):
        try:
            self.engine = pyttsx3.init()
            self.engine.setProperty('rate', self.rate)
            # Try to set voice
            voices = self.engine.getProperty('voices')
            for v in voices:
                if self.current_voice_id in v.id or self.current_voice_id == v.name:
                    self.engine.setProperty('voice', v.id)
                    break
        except Exception as e:
            print(f"TTS Init Error: {e}")

    def get_voices(self):
        if self.engine:
            return self.engine.getProperty('voices')
        return []

    def get_current_voice_id(self):
        return self.current_voice_id

    def get_rate(self):
        return self.rate

    def set_voice(self, voice_id):
        self.current_voice_id = voice_id
        config_manager.set("voice_id", voice_id)
        if self.engine:
            try:
                self.engine.setProperty('voice', voice_id)
            except:
                pass

    def set_speed(self, rate):
        self.rate = rate
        config_manager.set("voice_speed", rate)
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
            except:
                pass

    def stop(self):
        if self.process and self.process.poll() is None:
            self.process.terminate()
            self.process = None

    def speak(self, text):
        if not text:
            return
            
        print(f"NOVA: {text}")
        self.stop()
        
        # macOS Native 'say'
        if sys.platform == "darwin":
            try:
                cmd = ["say", text]
                
                # Resolve Voice Name for 'say' command
                voice_name = None
                # If ID is something like "com.apple.speech.synthesis.voice.Victoria", extract "Victoria"
                if "voice." in self.current_voice_id:
                     voice_name = self.current_voice_id.split(".")[-1]
                else:
                     voice_name = self.current_voice_id
                
                if voice_name:
                    cmd.extend(["-v", voice_name])
                
                if self.rate:
                    cmd.extend(["-r", str(self.rate)])

                self.process = subprocess.Popen(cmd)
                try:
                    # Wait up to 15 seconds (or roughly 1s per 10 chars? No, hard limit for now)
                    # For long responses, 15s might cut it off. 
                    # But if it hangs, we need to abort. 
                    # Let's use a generous 30s timeout? 
                    # Or calculate based on length: len(text) / 15 chars/sec
                    timeout = max(5, len(text) / 10) 
                    self.process.wait(timeout=timeout)
                except subprocess.TimeoutExpired:
                    print("TTS Timeout. Terminating.")
                    self.stop()
                return
            except Exception as e:
                print(f"Mac 'say' Error: {e}")
        
        # Fallback
        if self.engine:
            self.engine.say(text)
            self.engine.runAndWait()

import pvporcupine
import pyaudio
import struct
import os
import threading
from dotenv import load_dotenv
from NOVA.core.config_manager import config_manager

load_dotenv()

class WakeWordListener:
    def __init__(self, callback=None, sensitivity=None):
        self.access_key = os.getenv("PORCUPINE_ACCESS_KEY")
        self.keywords = ["jarvis"]
        
        # Load from config if not passed
        if sensitivity is None:
            self.sensitivity = config_manager.get("wake_word_sensitivity", 0.5)
        else:
            self.sensitivity = sensitivity
        
        self.callback = callback
        self.is_listening = False
        self.thread = None
        
        self.porcupine = None
        self.pa = None
        self.audio_stream = None
        
        if not self.access_key:
             print("WARNING: PORCUPINE_ACCESS_KEY not found.")

    def _init_porcupine(self):
        try:
            self.porcupine = pvporcupine.create(
                access_key=self.access_key,
                keywords=self.keywords,
                sensitivities=[self.sensitivity] * len(self.keywords)
            )
            self.pa = pyaudio.PyAudio()
            self.audio_stream = self.pa.open(
                rate=self.porcupine.sample_rate,
                channels=1,
                format=pyaudio.paInt16,
                input=True,
                frames_per_buffer=self.porcupine.frame_length
            )
        except Exception as e:
            print(f"Wake Word Init Error: {e}")

    def start(self):
        if self.is_listening:
            return
            
        if not self.access_key:
            print("Cannot start Porcupine: No Access Key.")
            return

        self.is_listening = True
        self.thread = threading.Thread(target=self._listen_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.is_listening = False
        if self.thread:
            # We can't easily join daemon threads blocked on I/O without a timeout/logic
            self.thread.join(timeout=0.5)
        self.cleanup()

    def _listen_loop(self):
        self._init_porcupine()
        print(f"Listening for wake word (Jarvis)... [Sens: {self.sensitivity}]")
        
        while self.is_listening:
            if not self.audio_stream or not self.porcupine:
                break
                
            try:
                pcm = self.audio_stream.read(self.porcupine.frame_length, exception_on_overflow=False)
                pcm = struct.unpack_from("h" * self.porcupine.frame_length, pcm)
                keyword_index = self.porcupine.process(pcm)
                
                if keyword_index >= 0:
                    print("Wake Word Detected!")
                    if self.callback:
                        # Pause listening while callback runs (optional, depends on callback)
                        # Usually we want to stop listening to allow mic access by STT
                        self.audio_stream.stop_stream()
                        self.audio_stream.close()
                        self.audio_stream = None
                        
                        self.callback() 
                        
                        # Re-open after callback returns
                        print("Resuming wake word listener...")
                        self.audio_stream = self.pa.open(
                            rate=self.porcupine.sample_rate,
                            channels=1,
                            format=pyaudio.paInt16,
                            input=True,
                            frames_per_buffer=self.porcupine.frame_length
                        )
            except Exception as e:
                print(f"WakeWord Loop Error: {e}")
                break
        
        self.cleanup()

    def update_sensitivity(self, new_sensitivity):
        print(f"Updating Sensitivity to {new_sensitivity}")
        self.sensitivity = new_sensitivity
        config_manager.set("wake_word_sensitivity", new_sensitivity)
        
        # Restart if running
        was_running = self.is_listening
        if was_running:
            self.stop()
            self.start()

    def cleanup(self):
        if self.audio_stream:
            self.audio_stream.close()
            self.audio_stream = None
        if self.porcupine:
            self.porcupine.delete()
            self.porcupine = None
        if self.pa:
            self.pa.terminate()
            self.pa = None

import sys
import os

# Add parent directory to sys.path to allow 'from NOVA...' imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import threading
from PyQt5 import QtWidgets, QtCore, QtGui
# New UI Import
from ui.main_window import NovaMainWindow

# fix warning
os.environ["TOKENIZERS_PARALLELISM"] = "false"

# Core Imports
from NOVA.core.wake_word import WakeWordListener
from NOVA.core.stt import WhisperSTT
from NOVA.core.nlp import NLPHandler
from NOVA.core.skill_manager import SkillManager
from NOVA.core.tts import TTSModule
from NOVA.core.memory_manager import MemoryManager
from NOVA.core.logger import logger

class NovaWorker(QtCore.QObject):
    # handles the pipeline and signals
    # signals: text, response, status, state, etc
    text_recognized = QtCore.pyqtSignal(str)
    response_ready = QtCore.pyqtSignal(str)
    status_update = QtCore.pyqtSignal(str)
    state_change = QtCore.pyqtSignal(str) # idle, listening, processing
    request_speech = QtCore.pyqtSignal(str) # New signal for TTS on main thread
    log_message = QtCore.pyqtSignal(str, str) # msg, level
    skill_status = QtCore.pyqtSignal(str, str) # skill_name, status ('active', 'success', 'error')
    token_received = QtCore.pyqtSignal(str) # For streaming text
    timeline_update = QtCore.pyqtSignal(str, str) # step, status

    def __init__(self):
        super().__init__()
        self.wake_word_listener = None
        self.stt = WhisperSTT()
        self.nlp = NLPHandler()
        self.skill_manager = SkillManager("features")
        self.tts = TTSModule()
        self.memory = MemoryManager()
        self.is_running = False
        self.current_state = "idle"
        self.stop_requested = False
        
        # Connect Scheduler
        scheduler = self.skill_manager.get_skill("SchedulerSkill")
        if scheduler:
            scheduler.trigger_notification.connect(self.handle_notification)
            
        # Connect System Skill
        sys_skill = self.skill_manager.get_skill("SystemSkill")
        if sys_skill:
            sys_skill.request_reload.connect(self.skill_manager.reload_skills)
            sys_skill.request_log_level.connect(self.handle_log_level)
            
        # Connect Workflow Skill
        wf_skill = self.skill_manager.get_skill("WorkflowSkill")
        if wf_skill:
            wf_skill.request_workflow_execution.connect(self.handle_workflow_execution)
            
        # Connect Reasoning Skill
        reasoning_skill = self.skill_manager.get_skill("ReasoningSkill")
        if reasoning_skill:
            reasoning_skill.request_sequence.connect(self.handle_workflow_execution)
        
        # Connect TTS signal to the speak method to ensure it runs on the main thread (where worker lives)
        # Connect TTS signal to the speak method to ensure it runs on the main thread (where worker lives)
        self.request_speech.connect(self.run_tts)

    def run_tts(self, text):
        # run tts on main thread
        self.tts.speak(text)
        self.state_change.emit("idle") # Finish speaking state
        
    def handle_notification(self, message, notif_type):
        self.status_update.emit(f"ALARM: {message}")
        # Speak it
        self.tts.speak(f"Attention: {message}")
        self.response_ready.emit(f"🔔 Reminder: {message}")

    def handle_log_level(self, level_str):
        import logging
        from NOVA.core.logger import logger
        lvl = getattr(logging, level_str.upper(), logging.INFO)
        logger.setLevel(lvl)
        self.log_message.emit(f"Log Level changed to {level_str}", "INFO")
        
    def handle_workflow_execution(self, steps):
        import time
        self.log_message.emit(f"Starting Workflow with {len(steps)} steps.", "INFO")
        self.response_ready.emit(f"Executing workflow with {len(steps)} steps.")
        # Wait for TTS
        time.sleep(2)
        
        for i, step in enumerate(steps):
             if self.stop_requested: break
             self.log_message.emit(f"Workflow Step {i+1}: {step}", "INFO")
             time.sleep(1)
             self.process_text_logic(step)

    def update_sensitivity(self, value):
        if self.wake_word_listener:
            # Value is 0-100 from slider, map to 0.0 - 1.0
            sens = value / 100.0
            self.wake_word_listener.update_sensitivity(sens)

    def start_listening(self):
        self.status_update.emit("Initializing Wake Word Listener...")
        self.wake_word_listener = WakeWordListener(callback=self.on_wake_word)
        self.wake_word_listener.start()
        self.status_update.emit("Listening for 'Jarvis'...")
        self.state_change.emit("idle") # Visual state
        self.is_running = True

    def stop_listening(self):
        if self.wake_word_listener:
            self.wake_word_listener.stop()
        self.is_running = False
        self.status_update.emit("Stopped.")
        self.state_change.emit("idle")
    

    def run_conversation_cycle(self, manual_text=None):
        """
        Runs one turn of the conversation: Listen -> Think -> Speak -> Relisten if needed.
        """
        self.status_update.emit("Listening for follow-up...")
        self.state_change.emit("listening") 
        self.process_command(manual_text)

    def handle_text_input(self, text):
        """
        Process text directly (e.g. from Custom Command box).
        """
        self.process_command(manual_text=text)

    def handle_mic_toggle(self):
        if self.current_state == "listening":
            self.log_message.emit("Mic Button: Stop Requested.", "INFO")
            self.stop_requested = True
            # We can't easily kill the STT thread, but we can ignore its result.
            self.state_change.emit("idle") # Visual feedback immediately
            self.current_state = "idle"
            
        elif self.current_state == "idle":
            self.log_message.emit("Mic Button: Start Listening.", "INFO")
            self.stop_requested = False
            # Run in thread to not block UI
            threading.Thread(target=self.run_manual_listen).start()

    def run_manual_listen(self):
        # Pause Wake Word if running (it might be running in background)
        # But wait, wake word loop uses PyAudio stream. 
        # If we interpret, we might conflict.
        # Ideally we temporarily pause wake word.
        if self.wake_word_listener:
            self.wake_word_listener.stop() # Stops loop, closes stream
            
        self.on_wake_word(manual_trigger=True)
        
        # Restart Wake Word
        if self.is_running and self.wake_word_listener:
             threading.Thread(target=self.wake_word_listener.start).start()

    def on_wake_word(self, manual_trigger=False):
        """
        Callback from WakeWordListener thread OR manual trigger.
        """
        if not manual_trigger:
             self.status_update.emit("Wake Word Detected!")
        
        self.process_command_thread()

    def process_command_thread(self):
        # Determine if we need to spawn a thread (if called from WakeWord callback, we are already in thread)
        # If called from manual trigger (which spawned a thread), we are in thread.
        # So we can just run blocking code.
        
        self.current_state = "listening"
        self.state_change.emit("listening") 
        self.status_update.emit("Listening...")
        self.timeline_update.emit("LISTEN", "ACTIVE")
        
        # 1. STT
        if self.stop_requested:
             self._reset_to_idle()
             return

        text = self.stt.transcribe() # Blocking 5-10s
        
        if self.stop_requested:
             self.log_message.emit("Action Aborted by User.", "INFO")
             self._reset_to_idle()
             return
             
        if not text:
             # If nothing heard, just exit
             self._reset_to_idle()
             return
             
        # ... Continue pipeline ...
        self.process_text_logic(text)
        self._reset_to_idle()

    def _reset_to_idle(self):
        self.current_state = "idle"
        self.state_change.emit("idle")
        self.timeline_update.emit("LISTEN", "DONE")

    def process_command(self, manual_text=None):
        # Legacy entry point, refactored to support threads
        if manual_text:
            self.process_text_logic(manual_text)
        else:
            self.process_command_thread()

    def process_text_logic(self, text):
        """
        Core logic for processing a string command.
        Decoupled from STT to allow workflow automation.
        """
        self.text_recognized.emit(text) # Update User Bubble

        # 2. Logic & Routing
        self.log_message.emit(f"Processing text: '{text}'", "DEBUG")
        
        # Use SkillManager's smart routing (NLP + Fallback)
        try:
             # Capture start time for accurate latency logging in UI
             import time
             t0 = time.time()
             skill_response = self.skill_manager.route_request(text)
             latency = (time.time() - t0) * 1000
             
             if skill_response:
                  intent = getattr(skill_response, 'intent', 'unknown')
                  self.log_message.emit(f"Routing Complete: Intent='{intent}' | Latency={latency:.1f}ms", "INFO")
             
        except Exception as e:
             self.log_message.emit(f"Routing Error: {e}", "ERROR")
             skill_response = None


        if not skill_response:
             self.log_message.emit("Skill execution failed (returned None)", "WARNING")
             self.state_change.emit("idle")
             return

        # Handle new SkillResponse object
        response_text = skill_response.text
        intent = skill_response.intent # Extract intent for local logic
        success = getattr(skill_response, 'success', True)
        
        # Skill Card Feedback
        skill_map = {
            "get_weather": "Weather",
            "reload_skills": "System",
            "set_log_level": "System",
            "get_time": "Date & Time", 
            "get_date": "Date & Time",
            "set_alarm": "Date & Time",
            "set_reminder": "Date & Time",
            "create_workflow": "Workflows",
            "run_workflow": "Workflows",
            "decompose_task": "Workflows"
        }
        card_name = skill_map.get(intent)
        if card_name:
             status = "success" if success else "error"
             self.skill_status.emit(card_name, status)
        
        # STREAMING LOGIC
        if getattr(skill_response, 'is_streaming', False) and skill_response.iterator:
            self.log_message.emit("Starting LLM Stream...", "DEBUG")
            # Signal UI to prepare for stream (clears bubble or creates new one)
            # We reuse response_ready with empty string to create the bubble?
            # Adjust window logic: response_ready(str) creates a bubble with that text.
            # If we send empty, it's an empty bubble.
            self.response_ready.emit("") 
            
            full_text = ""
            try:
                for chunk in skill_response.iterator:
                    if chunk:
                        full_text += chunk
                        self.token_received.emit(chunk)
                        # Minimal delay for effect if local? No, let it fly.
                
                response_text = full_text # Update final text
                # We do NOT emit response_ready again, or we'd duplicate.
                
            except Exception as e:
                self.log_message.emit(f"Streaming Error: {e}", "ERROR")
                response_text = "Error streaming response."
                self.response_ready.emit(response_text) # Fallback
        else:
            # Standard non-streaming
            self.response_ready.emit(response_text) 
        
        # 4. Memory
        self.memory.save_context(text, response_text)

        # 5. TTS (Direct Call for Synchronization)
        self.status_update.emit("Speaking...")
        # Update connection to Timeline
        self.timeline_update.emit("SPEAK", "ACTIVE") 
        
        if self.tts:
            self.tts.speak(response_text)
        else:
            self.request_speech.emit(response_text)

        self.timeline_update.emit("SPEAK", "DONE")
            
        # 6. Check for Follow-up / Reprompt
        if response_text.strip().endswith("?") or response_text.strip().endswith("..."):
             print("Detected question, listening for follow-up...")
             self.run_conversation_cycle()
             return

        if intent == "exit":
            self.stop_listening()
            QtCore.QCoreApplication.quit()

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    
    # Fix for "MS Shell Dlg 2" warning on Mac
    font = QtGui.QFont("Arial", 10)
    app.setFont(font)
    
    # Initialize Main Window
    window = NovaMainWindow()
    
    # Initialize Worker
    worker = NovaWorker()
    
    # Inject TTS module into Window for Settings usage
    window.tts_module = worker.tts
    
    # Connect Signals to GUI Slots
    worker.status_update.connect(window.update_status)
    worker.state_change.connect(window.set_state)
    worker.log_message.connect(window.log_message)
    worker.skill_status.connect(window.set_skill_status)
    
    # Connect Chat Bubbles
    worker.text_recognized.connect(lambda t: window.add_chat_message(t, True))  # User
    worker.response_ready.connect(lambda t: window.add_chat_message(t, False)) # Nova
    
    # Streaming & Timeline
    worker.token_received.connect(window.update_chat_stream)
    worker.timeline_update.connect(getattr(window.timeline, 'set_step_status', lambda x,y: None))
    
    # Connect Custom Command Input
    # We need to bridge the window's signal (if we made one) or just manually call worker method
    # Since window.run_custom_command Logic is inside window, we should make window emit a signal 
    # Or simpler: Make window call worker directly? No, decoupling is better.
    # Let's overwrite `run_custom_command` in window (monkey patch) or just connect a lambda?
    # Window.run_custom_command currently just adds text to chat. We need it to trigger worker.
    # Best way: Window emits `command_entered(str)`, Main connects it to `worker.handle_text_input`.
    
    # Since I cannot easily edit `ui/main_window.py` again just to add a signal without re-writing it,
    # I will modify `main_window.py`'s `run_custom_command` to EMIT a signal.
    # Wait, I declared `run_custom_command` in `ui/main_window.py` as a slot but it doesn't emit.
    # I will just override the method instance for now or connect the `custom_cmd_input.returnPressed` 
    # to a local function right here.
    
    def on_custom_command():
        cmd = window.custom_cmd_input.text()
        if cmd:
            window.custom_cmd_input.clear()
            # window.add_chat_message(cmd, True) # Worker will emit this back via text_recognized
    # Disconnect existing if any (none yet) and connect to our logic
    try:
        window.custom_cmd_input.returnPressed.disconnect()
    except:
        pass
    # Connect GUI Signals
    window.custom_cmd_input.returnPressed.connect(lambda: worker.handle_text_input(window.custom_cmd_input.text()))
    window.sensitivity_changed.connect(worker.update_sensitivity)
    
    # NEW: Connect Quick Actions and Restart
    window.command_requested.connect(worker.handle_text_input)
    window.mic_toggled.connect(worker.handle_mic_toggle)

    # Start Logic
    worker.start_listening()
    
    window.show()
    sys.exit(app.exec_())

from PyQt5 import QtWidgets, QtCore
from NOVA.core.config_manager import config_manager
from NOVA.core.persona import persona_manager

class SettingsDialog(QtWidgets.QDialog):
    sensitivity_changed = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None, tts_module=None):
        super().__init__(parent)
        self.tts_module = tts_module
        self.setWindowTitle("NOVA Settings")
        self.resize(400, 500)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        
        # Tabs
        tabs = QtWidgets.QTabWidget()
        layout.addWidget(tabs)
        
        # --- General Tab ---
        general_tab = QtWidgets.QWidget()
        gen_layout = QtWidgets.QVBoxLayout(general_tab)
        
        # Memory Toggle
        self.memory_cb = QtWidgets.QCheckBox("Enable Memory (ChromaDB)")
        self.memory_cb.setChecked(True)
        gen_layout.addWidget(self.memory_cb)
        
        # Debug Logs
        self.debug_cb = QtWidgets.QCheckBox("Show Debug Logs")
        self.debug_cb.setChecked(True)
        gen_layout.addWidget(self.debug_cb)
        
        gen_layout.addStretch()
        tabs.addTab(general_tab, "General")
        
        # --- Voice Tab ---
        voice_tab = QtWidgets.QWidget()
        voice_layout = QtWidgets.QVBoxLayout(voice_tab)
        
        # Wake Word Sensitivity
        voice_layout.addWidget(QtWidgets.QLabel("Wake Word Sensitivity:"))
        self.sens_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.sens_slider.setRange(0, 100)
        
        # Load from config
        saved_sens = config_manager.get("wake_word_sensitivity", 0.5)
        self.sens_slider.setValue(int(saved_sens * 100))
        
        voice_layout.addWidget(self.sens_slider)
        
        # Wake Word Model
        voice_layout.addWidget(QtWidgets.QLabel("Wake Word Model:"))
        self.wake_word_model_combo = QtWidgets.QComboBox() # Renamed from stt_combo to avoid conflict
        self.wake_word_model_combo.addItems(["Porcupine (Local)", "Whisper (Local)"]) # Example items
        voice_layout.addWidget(self.wake_word_model_combo)

        # STT Provider
        voice_layout.addWidget(QtWidgets.QLabel("STT Provider:"))
        self.stt_combo = QtWidgets.QComboBox()
        self.stt_combo.addItems(["Whisper (Local)", "Google (Cloud)"])
        voice_layout.addWidget(self.stt_combo)
        
        # Voice Selection (New)
        voice_layout.addWidget(QtWidgets.QLabel("System Voice:"))
        self.voice_combo = QtWidgets.QComboBox()
        self.voices = []
        if self.tts_module:
            self.voices = self.tts_module.get_voices()
            current_id = self.tts_module.get_current_voice_id()
            current_idx = 0
            
            for i, v in enumerate(self.voices):
                self.voice_combo.addItem(f"{v.name}")
                if current_id and v.id == current_id:
                    current_idx = i
            
            self.voice_combo.setCurrentIndex(current_idx)
        
        voice_layout.addWidget(self.voice_combo)

        # TTS Provider (Placeholder for now)
        voice_layout.addWidget(QtWidgets.QLabel("TTS Engine:"))
        self.tts_combo = QtWidgets.QComboBox()
        self.tts_combo.addItems(["pyttsx3 (Offline)", "ElevenLabs (API)", "Coqui (Local)"])
        voice_layout.addWidget(self.tts_combo)
        
        # Speed Slider
        voice_layout.addWidget(QtWidgets.QLabel("Voice Speed:"))
        self.speed_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.speed_slider.setRange(50, 300) # Increased range
        
        if self.tts_module:
            current_speed = self.tts_module.get_rate()
            self.speed_slider.setValue(int(current_speed))
        else:
            self.speed_slider.setValue(200)
            
        voice_layout.addWidget(self.speed_slider)
        
        # Pitch Slider
        voice_layout.addWidget(QtWidgets.QLabel("Voice Pitch:"))
        self.pitch_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.pitch_slider.setRange(50, 200)
        self.pitch_slider.setValue(100)
        voice_layout.addWidget(self.pitch_slider)
        
        voice_layout.addStretch()
        tabs.addTab(voice_tab, "Voice")

        # --- Persona Tab ---
        persona_tab = QtWidgets.QWidget()
        persona_layout = QtWidgets.QVBoxLayout(persona_tab)
        
        persona_layout.addWidget(QtWidgets.QLabel("System Prompt (Persona):"))
        self.persona_edit = QtWidgets.QTextEdit()
        self.persona_edit.setPlaceholderText("You are NOVA...")
        self.persona_edit.setText(persona_manager.get_prompt())
        persona_layout.addWidget(self.persona_edit)
        
        # Reset Button
        reset_btn = QtWidgets.QPushButton("Reset to Default")
        reset_btn.clicked.connect(lambda: self.persona_edit.setText(persona_manager.DEFAULT_SYSTEM_PROMPT))
        persona_layout.addWidget(reset_btn)
        
        tabs.addTab(persona_tab, "Persona")
        
        # --- Buttons ---
        btn_box = QtWidgets.QHBoxLayout()
        save_btn = QtWidgets.QPushButton("Save")
        save_btn.clicked.connect(self.accept)
        cancel_btn = QtWidgets.QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        
        btn_box.addStretch()
        btn_box.addWidget(cancel_btn)
        btn_box.addWidget(save_btn)
        
        layout.addLayout(btn_box)

    def accept(self):
        # Apply Changes
        if self.tts_module:
             # Apply Voice
             idx = self.voice_combo.currentIndex()
             if idx >= 0 and idx < len(self.voices):
                 selected_voice = self.voices[idx]
                 self.tts_module.set_voice(selected_voice.id)
            
             # Apply Speed
             speed = self.speed_slider.value()
             self.tts_module.set_speed(speed)
             
        # Apply Sensitivity
        self.sensitivity_changed.emit(self.sens_slider.value())
        
        # Apply Persona
        persona_manager.set_prompt(self.persona_edit.toPlainText())
            
        super().accept()

        # Style
        self.setStyleSheet("""
            QDialog { background-color: #2d2d30; color: white; }
            QLabel { color: white; }
            QCheckBox { color: white; }
            QTabWidget::pane { border: 1px solid #3e3e42; }
            QTabBar::tab { background: #252526; color: white; padding: 5px; }
            QTabBar::tab:selected { background: #3e3e42; }
        """)

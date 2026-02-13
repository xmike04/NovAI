import sys
from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

from ui.styles import quantum_style
from ui.chat_bubble import ChatBubble
from ui.settings_dialog import SettingsDialog
from ui.widgets.waveform import WaveformVisualizer
from ui.widgets.skill_card import SkillCard
from ui.widgets.debug_console import DebugConsole
from ui.widgets.timeline import TimelineWidget

class NovaMainWindow(QtWidgets.QMainWindow):
    sensitivity_changed = QtCore.pyqtSignal(int)
    command_requested = QtCore.pyqtSignal(str) # New signal
    mic_toggled = QtCore.pyqtSignal() # New signal

    def __init__(self):
        super().__init__()
        self.setWindowTitle("NOVA 2.0 - Quantum Interface")
        self.resize(1200, 800)
        self.setStyleSheet(quantum_style)
        
        # Central Widget
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        
        self.root_layout = QtWidgets.QVBoxLayout(central_widget)
        self.root_layout.setContentsMargins(0, 0, 0, 0)
        self.root_layout.setSpacing(0)
        
        # --- 0. HEADER ---
        self.create_header()
        
        # --- 1. MAIN SPLITTER ---
        splitter_layout = QtWidgets.QHBoxLayout()
        splitter_layout.setSpacing(0)
        self.root_layout.addLayout(splitter_layout)
        
        # LEFT PANEL (Chat)
        self.create_left_panel()
        splitter_layout.addWidget(self.left_panel)
        
        # CENTER PANEL (Stage)
        self.create_center_stage()
        splitter_layout.addWidget(self.center_panel)
        
        # RIGHT PANEL (Control Deck)
        self.create_right_panel()
        splitter_layout.addWidget(self.right_panel)

        # NOTE: Debug Console is added to root_layout below the splitter
        self.debug_console = DebugConsole()
        self.debug_console.hide() # Hidden by default
        self.debug_console.setFixedHeight(200)
        self.root_layout.addWidget(self.debug_console)

    def create_header(self):
        self.header_frame = QtWidgets.QFrame()
        self.header_frame.setObjectName("header_frame")
        self.header_frame.setFixedHeight(60)
        layout = QtWidgets.QHBoxLayout(self.header_frame)
        layout.setContentsMargins(20, 0, 20, 0)
        
        # Logo
        logo = QtWidgets.QLabel("NOVA AI")
        logo.setObjectName("logo_label")
        layout.addWidget(logo)
        
        layout.addStretch()
        
        # Status
        self.status_label = QtWidgets.QLabel("SYSTEM ONLINE")
        self.status_label.setObjectName("status_label")
        layout.addWidget(self.status_label)
        
        # Settings Icon
        layout.addSpacing(20)
        self.settings_btn = QtWidgets.QPushButton()
        self.settings_btn.setIcon(qta.icon('fa5s.cog', color='white'))
        self.settings_btn.setFixedSize(40, 40)
        self.settings_btn.clicked.connect(self.open_settings)
        self.settings_btn.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.settings_btn)

        # Debug Toggle
        self.debug_btn = QtWidgets.QPushButton()
        self.debug_btn.setIcon(qta.icon('fa5s.terminal', color='gray'))
        self.debug_btn.setFixedSize(40, 40)
        self.debug_btn.setCheckable(True)
        self.debug_btn.clicked.connect(self.toggle_debug)
        self.debug_btn.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(self.debug_btn)
        
        self.root_layout.addWidget(self.header_frame)

    def create_center_stage(self):
        self.center_panel = QtWidgets.QWidget()
        self.center_panel.setStyleSheet("background-color: #121212;")
        layout = QtWidgets.QVBoxLayout(self.center_panel)
        layout.setAlignment(QtCore.Qt.AlignCenter)
        
        # Stacked Widget for changing states
        self.stage_stack = QtWidgets.QStackedWidget()
        self.stage_stack.setFixedSize(500, 400)
        
        # Page 0: Idle (Logo Only)
        self.page_idle = QtWidgets.QWidget()
        idle_layout = QtWidgets.QVBoxLayout(self.page_idle)
        # Using Icon instead of Emoji
        idle_logo = QtWidgets.QLabel()
        idle_logo.setPixmap(qta.icon('fa5s.microchip', color='#00d4ff').pixmap(100, 100))
        idle_logo.setAlignment(QtCore.Qt.AlignCenter)
        idle_layout.addWidget(idle_logo)
        idle_label = QtWidgets.QLabel("Awaiting Input")
        idle_label.setAlignment(QtCore.Qt.AlignCenter)
        idle_layout.addWidget(idle_label)
        self.stage_stack.addWidget(self.page_idle)
        
        # Page 1: Waveform (Listening)
        self.waveform = WaveformVisualizer()
        self.stage_stack.addWidget(self.waveform)
        
        # Page 2: Processing (Spinner)
        self.page_process = QtWidgets.QWidget()
        proc_layout = QtWidgets.QVBoxLayout(self.page_process)
        proc_icon = QtWidgets.QLabel()
        proc_icon.setPixmap(qta.icon('fa5s.spinner', color='#00d4ff', animation=qta.Spin(self.page_process)).pixmap(64,64))
        proc_icon.setAlignment(QtCore.Qt.AlignCenter)
        proc_layout.addWidget(proc_icon)
        proc_label = QtWidgets.QLabel("Thinking...")
        proc_label.setAlignment(QtCore.Qt.AlignCenter)
        proc_layout.addWidget(proc_label)
        self.stage_stack.addWidget(self.page_process)
        
        layout.addWidget(self.stage_stack)
        
        # Transcription Label (Subtitles)
        self.subtitle_label = QtWidgets.QLabel("")
        self.subtitle_label.setStyleSheet("font-size: 18px; color: #00d4ff; margin-top: 20px;")
        self.subtitle_label.setAlignment(QtCore.Qt.AlignCenter)
        self.subtitle_label.setWordWrap(True)
        layout.addWidget(self.subtitle_label)

        # Timeline
        self.timeline = TimelineWidget()
        layout.addWidget(self.timeline)

    def create_left_panel(self):
        self.left_panel = QtWidgets.QWidget()
        self.left_panel.setObjectName("left_panel")
        self.left_panel.setFixedWidth(320)
        layout = QtWidgets.QVBoxLayout(self.left_panel)
        layout.setContentsMargins(10, 10, 10, 10)
        
        self.chat_list = QtWidgets.QListWidget()
        self.chat_list.setVerticalScrollMode(QtWidgets.QAbstractItemView.ScrollPerPixel)
        self.chat_list.itemClicked.connect(self.on_history_click)
        layout.addWidget(self.chat_list)

    def create_right_panel(self):
        self.right_panel = QtWidgets.QWidget()
        self.right_panel.setObjectName("right_panel")
        self.right_panel.setFixedWidth(260)
        layout = QtWidgets.QVBoxLayout(self.right_panel)
        layout.setContentsMargins(15, 15, 15, 15)
        
        layout.addWidget(QtWidgets.QLabel("MODULES"))
        
        # Skill Cards
        self.skill_cards = {}
        skills = [
            ("Weather", "fa5s.cloud-sun"), 
            ("System", "fa5s.microchip"), 
            ("Date & Time", "fa5s.clock"), 
            ("Workflows", "fa5s.project-diagram")
        ]
        
        for name, icon in skills:
            card = SkillCard(name, icon)
            card.clicked.connect(self.handle_quick_action)
            layout.addWidget(card)
            self.skill_cards[name.lower()] = card
            
        layout.addStretch()
        
        # Duo Mic Button
        self.mic_btn = QtWidgets.QPushButton("LISTEN")
        self.mic_btn.setIcon(qta.icon('fa5s.microphone', color='white'))
        self.mic_btn.setFixedSize(230, 50) # Full width-ish
        self.mic_btn.setStyleSheet("""
            QPushButton {
                background-color: #00d4ff; 
                color: #000000; 
                font-size: 16px; 
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover { background-color: #00c0e0; }
        """)
        self.mic_btn.clicked.connect(self.toggle_mic)
        layout.addWidget(self.mic_btn)
        
        layout.addSpacing(20)
        
        layout.addWidget(QtWidgets.QLabel("COMMAND OVERRIDE"))
        self.custom_cmd_input = QtWidgets.QLineEdit()
        self.custom_cmd_input.setPlaceholderText("Enter command...")
        layout.addWidget(self.custom_cmd_input)
        
        restart_btn = QtWidgets.QPushButton("RESTART CORE")
        restart_btn.clicked.connect(self.restart_assistant)
        layout.addWidget(restart_btn)

    def set_skill_status(self, skill_name, status):
        """
        Highlight a skill card. 
        skill_name: 'weather', 'system', etc.
        status: 'active', 'success', 'error', 'idle'
        """
        # Reset all first if active? Or just set one?
        if status == "active":
            for card in self.skill_cards.values():
                card.set_status("idle")
                
        # Find partial match if exact key missing
        key = skill_name.lower().replace("skill", "").strip()
        
        if key in self.skill_cards:
            self.skill_cards[key].set_status(status)
            
            # Auto-reset success/error after a delay?
            if status in ["success", "error"]:
                QtCore.QTimer.singleShot(3000, lambda: self.skill_cards[key].set_status("idle"))

    # --- SLOTS ---
    
    def set_state(self, state):
        if state == "listening":
            self.stage_stack.setCurrentIndex(1)
            self.waveform.set_active(True)
            self.status_label.setText("LISTENING")
            self.status_label.setStyleSheet("color: #00ff88;") # Green
            self.timeline.set_step_status("LISTEN", "ACTIVE")
            
            # Update Mic Button
            self.mic_btn.setText("STOP")
            self.mic_btn.setIcon(qta.icon('fa5s.stop', color='white'))
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ff4444; 
                    color: #ffffff; 
                    font-size: 16px; 
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #ff2222; }
            """)
            
        elif state == "processing":
            self.stage_stack.setCurrentIndex(2)
            self.waveform.set_active(False)
            self.status_label.setText("PROCESSING")
            self.status_label.setStyleSheet("color: #00d4ff;") # Blue
            self.timeline.set_step_status("THINK", "ACTIVE")
            
        elif state == "speaking": # Assuming you might add this state explicitly
             self.timeline.set_step_status("SPEAK", "ACTIVE")
             
        else: # Idle
            self.stage_stack.setCurrentIndex(0)
            self.waveform.set_active(False)
            self.status_label.setText("SYSTEM ONLINE")
            self.status_label.setStyleSheet("color: #888888;")
            # Don't reset timeline immediately so user can see 'Done'? 
            # Or reset? Let's reset for now or keep 'SPEAK' as done.
            if self.timeline.current_step == 3: # If was speaking
                 self.timeline.set_step_status("SPEAK", "DONE")
            else:
                 self.timeline.reset()

            # Reset Mic Button
            self.mic_btn.setText("LISTEN")
            self.mic_btn.setIcon(qta.icon('fa5s.microphone', color='white'))
            self.mic_btn.setStyleSheet("""
                QPushButton {
                    background-color: #00d4ff; 
                    color: #000000; 
                    font-size: 16px; 
                    border-radius: 8px;
                    font-weight: bold;
                }
                QPushButton:hover { background-color: #00c0e0; }
            """)

    def update_status(self, text):
        # Optional: showing subtle logs in header? 
        # For now, we prefer the status label to be stable state.
        pass

    def add_chat_message(self, text, is_sender):
        item = QtWidgets.QListWidgetItem()
        bubble = ChatBubble(text, is_sender)
        item.setSizeHint(bubble.sizeHint())
        self.chat_list.addItem(item)
        self.chat_list.setItemWidget(item, bubble)
        self.chat_list.scrollToBottom()
        
        if is_sender:
            self.subtitle_label.setText(f'"{text}"')
        
        return bubble # Return for streaming

    def update_chat_stream(self, token):
        # find last bubble (assumed to be NOVA's because response_ready("") was called)
        count = self.chat_list.count()
        if count > 0:
            item = self.chat_list.item(count - 1)
            bubble = self.chat_list.itemWidget(item)
            if bubble:
                # Update Text
                current_text = bubble.label.text()
                new_text = current_text + token
                bubble.label.setText(new_text)
                # Resize
                bubble.adjustSize()
                item.setSizeHint(bubble.sizeHint())
                self.chat_list.scrollToBottom()

    def open_settings(self):
        tts = getattr(self, 'tts_module', None)
        dlg = SettingsDialog(self, tts_module=tts)
        # Forward signal
        dlg.sensitivity_changed.connect(self.sensitivity_changed.emit)
        dlg.exec_()
        
    def handle_quick_action(self, action):
        skill_map = {
            "Weather": "What's the weather?",
            "System": "System status", # Or reload
            "Date & Time": "What time is it?",
            "Workflow": "List workflows",
            "Workflows": "List workflows"
        }
        
        cmd = skill_map.get(action)
        if cmd:
            self.command_requested.emit(cmd)
        elif action == "Clear Log":
            self.chat_list.clear()
        
    def on_history_click(self, item):
        pass
        
    def restart_assistant(self):
        # Trigger system reload via command?
        # Or just exit?
        # User Button says "RESTART CORE"
        # Let's map it to "reload skills" or just exit app to let Supervisor restart it?
        # For now, let's map to internal reload command
        self.command_requested.emit("reload skills")

    def toggle_mic(self):
        self.mic_toggled.emit()

    def toggle_debug(self):
        if self.debug_btn.isChecked():
            self.debug_console.show()
            self.debug_btn.setIcon(qta.icon('fa5s.terminal', color='#00d4ff')) # Blue
        else:
            self.debug_console.hide()
            self.debug_btn.setIcon(qta.icon('fa5s.terminal', color='gray'))

    def log_message(self, message, level="INFO"):
        self.debug_console.log(message, level)
        # Also update status label if it's important
        if level in ["INFO", "ERROR"]:
            self.status_label.setText(str(message)[:30].upper())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = NovaMainWindow()
    window.show()
    sys.exit(app.exec_())

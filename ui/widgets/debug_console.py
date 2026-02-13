from PyQt5 import QtWidgets, QtCore, QtGui
import datetime

class DebugConsole(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
        
    def init_ui(self):
        layout = QtWidgets.QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header / Toolbar
        header_layout = QtWidgets.QHBoxLayout()
        label = QtWidgets.QLabel("DEBUG CONSOLE")
        label.setStyleSheet("font-weight: bold; color: #888;")
        header_layout.addWidget(label)
        
        clear_btn = QtWidgets.QPushButton("Clear")
        clear_btn.setFixedSize(60, 25)
        clear_btn.clicked.connect(self.clear_log)
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Text Area
        self.text_edit = QtWidgets.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.text_edit.setStyleSheet("""
            QTextEdit {
                background-color: #1e1e1e;
                color: #d4d4d4;
                border: 1px solid #3e3e42;
                font-family: 'Consolas', 'Monaco', monospace;
                font-size: 11px;
            }
        """)
        layout.addWidget(self.text_edit)
        
        # Default Filter (Show all)
        # Could add checkboxes here later
        
    def log(self, message, level="INFO"):
        """
        Appends a log message with color coding.
        """
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        color = "#d4d4d4" # Default White/Gray
        if level == "ERROR": color = "#f48771" # Red
        elif level == "WARNING": color = "#cca700" # Yellow
        elif level == "DEBUG": color = "#569cd6" # Blue
        elif level == "SUCCESS": color = "#89d185" # Green
        
        formatted_msg = f'<span style="color:#555;">[{timestamp}]</span> <span style="color:{color}; font-weight:bold;">[{level}]</span> {message}'
        
        self.text_edit.append(formatted_msg)
        
        # Auto-scroll
        cursor = self.text_edit.textCursor()
        cursor.movePosition(QtGui.QTextCursor.End)
        self.text_edit.setTextCursor(cursor)
        
    def clear_log(self):
        self.text_edit.clear()

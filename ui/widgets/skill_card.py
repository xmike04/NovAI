from PyQt5 import QtWidgets, QtCore
import qtawesome as qta

class SkillCard(QtWidgets.QFrame):
    clicked = QtCore.pyqtSignal(str)

    def __init__(self, title, icon_name, parent=None):
        super().__init__(parent)
        self.title = title
        self.setCursor(QtCore.Qt.PointingHandCursor)
        self.name = title
        
        # Layout
        layout = QtWidgets.QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # Icon
        self.icon_label = QtWidgets.QLabel()
        icon = qta.icon(icon_name, color="#00d4ff")
        self.icon_label.setPixmap(icon.pixmap(24, 24))
        layout.addWidget(self.icon_label)
        
        # Title
        self.title_label = QtWidgets.QLabel(title)
        self.title_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.title_label)
        
        layout.addStretch()
        
        # Style
        self.setStyleSheet("""
            SkillCard {
                background-color: #1a1a1a;
                border: 1px solid #333333;
                border-radius: 8px;
            }
            SkillCard:hover {
                background-color: #222222;
                border: 1px solid #00d4ff;
            }
        """)
        
    def mousePressEvent(self, event):
        self.clicked.emit(self.title)

    def set_status(self, status):
        """
        Update visual status: 'active', 'success', 'error', 'idle'
        """
        border_color = "#333333" # idle
        
        if status == "active":
            border_color = "#00d4ff" # Blue
        elif status == "success":
            border_color = "#00ff88" # Green
        elif status == "error":
            border_color = "#ff0055" # Red
            
        self.setStyleSheet(f"""
            SkillCard {{
                background-color: #1a1a1a;
                border: 2px solid {border_color};
                border-radius: 8px;
            }}
            SkillCard:hover {{
                background-color: #222222;
                border: 2px solid #00d4ff;
            }}
        """)

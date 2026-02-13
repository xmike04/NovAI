from PyQt5 import QtWidgets, QtCore, QtGui

class ChatBubble(QtWidgets.QWidget):
    def __init__(self, text, is_sender=False, parent=None):
        super().__init__(parent)
        self.text = text
        self.is_sender = is_sender  # True = User (Right), False = NOVA (Left)
        self.init_ui()

    def init_ui(self):
        layout = QtWidgets.QHBoxLayout()
        layout.setContentsMargins(10, 5, 10, 5) # Outer margins
        
        # Create the text label
        self.label = QtWidgets.QLabel(self.text)
        self.label.setWordWrap(True)
        self.label.setTextInteractionFlags(QtCore.Qt.TextSelectableByMouse)
        
        # Style the bubble
        if self.is_sender:
            # User Bubble (Right, Blue)
            self.label.setStyleSheet("""
                background-color: #007acc;
                color: white;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
            """)
            layout.addStretch() # Push to right
            layout.addWidget(self.label)
        else:
            # NOVA Bubble (Left, Dark Grey)
            self.label.setStyleSheet("""
                background-color: #3e3e42;
                color: white;
                border-radius: 12px;
                padding: 10px;
                font-size: 14px;
            """)
            layout.addWidget(self.label)
            layout.addStretch() # Push from right

        self.setLayout(layout)
        self.setSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Minimum)


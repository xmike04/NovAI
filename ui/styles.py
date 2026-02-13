quantum_style = """
QMainWindow {
    background-color: #121212;
}

QFrame {
    border: none;
}

QLabel {
    color: #e0e0e0;
    font-family: 'Arial', sans-serif;
    font-size: 14px;
}

/* Scrollbars */
QScrollBar:vertical {
    border: none;
    background: #1a1a1a;
    width: 8px;
    margin: 0px 0px 0px 0px;
}
QScrollBar::handle:vertical {
    background: #333333;
    min-height: 20px;
    border-radius: 4px;
}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    background: none;
}

/* List Widget (Chat) */
QListWidget {
    background-color: #121212;
    border: none;
    outline: none;
}

/* Inputs */
QLineEdit {
    background-color: #1a1a1a;
    color: #ffffff;
    border: 1px solid #333333;
    border-radius: 8px;
    padding: 10px;
    font-size: 14px;
}
QLineEdit:focus {
    border: 1px solid #00d4ff; /* NOVA Blue */
    background-color: #222222;
}

/* Buttons */
QPushButton {
    background-color: #1a1a1a;
    color: #00d4ff;
    border: 1px solid #333333;
    padding: 10px 16px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
}

QPushButton:hover {
    background-color: #222222;
    border: 1px solid #00d4ff;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #00d4ff;
    color: #121212;
}

/* Header */
QFrame#header_frame {
    background-color: #0f0f0f;
    border-bottom: 1px solid #222222;
}

/* Panels */
QWidget#left_panel {
    background-color: #121212;
    border-right: 1px solid #222222;
}
QWidget#right_panel {
    background-color: #151515;
    border-left: 1px solid #222222;
}

/* Status Label */
QLabel#status_label {
    color: #888888;
    font-weight: 500;
}

/* Logo */
QLabel#logo_label {
    color: #ffffff;
    font-size: 18px;
    font-weight: bold;
    letter-spacing: 1px;
}
"""

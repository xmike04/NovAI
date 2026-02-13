from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta

class TimelineWidget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(60)
        self.steps = ["LISTEN", "THINK", "ACT", "SPEAK"]
        self.current_step = -1 # -1 = Idle
        self.step_status = ["PENDING"] * 4 # PENDING, ACTIVE, DONE, ERROR
        
        # Animations or Timer for pulsing?
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update) # Trigger repaint for animations if needed
        # self.timer.start(50) 
        
    def set_step_status(self, step_name, status):
        if step_name in self.steps:
            idx = self.steps.index(step_name)
            self.step_status[idx] = status
            
            # Logic: If step 2 is active, step 0,1 should be DONE
            if status == "ACTIVE":
                self.current_step = idx
                for i in range(idx):
                    self.step_status[i] = "DONE"
                for i in range(idx + 1, len(self.steps)):
                    self.step_status[i] = "PENDING"
            
            self.update()
    
    def reset(self):
        self.current_step = -1
        self.step_status = ["PENDING"] * 4
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        w = self.width()
        h = self.height()
        
        margin = 40
        available_w = w - (margin * 2)
        step_dist = available_w / (len(self.steps) - 1)
        
        # Draw Line
        painter.setPen(QtGui.QPen(QtGui.QColor("#3e3e42"), 2))
        y = h // 2
        painter.drawLine(margin, y, w - margin, y)
        
        # Draw Progress Line
        if self.current_step >= 0:
            progress_w = step_dist * self.current_step
            # Animate? For now, snap.
            painter.setPen(QtGui.QPen(QtGui.QColor("#00d4ff"), 2))
            painter.drawLine(margin, y, int(margin + progress_w), y)

        # Draw Nodes
        for i, step in enumerate(self.steps):
            x = int(margin + (i * step_dist))
            status = self.step_status[i]
            
            # Color
            if status == "DONE":
                color = QtGui.QColor("#00ff88") # Green
            elif status == "ACTIVE":
                color = QtGui.QColor("#00d4ff") # Blue
            elif status == "ERROR":
                color = QtGui.QColor("#ff5555") # Red
            else: # PENDING
                color = QtGui.QColor("#3e3e42") # Gray
            
            # Draw Circle
            radius = 8
            if status == "ACTIVE": radius = 10
            
            painter.setBrush(color)
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawEllipse(QtCore.QPoint(x, y), radius, radius)
            
            # Draw Label
            painter.setPen(QtGui.QColor("#d4d4d4"))
            font = painter.font()
            font.setPointSize(8)
            painter.setFont(font)
            fm = QtGui.QFontMetrics(font)
            text_w = fm.width(step)
            painter.drawText(x - (text_w // 2), y + 25, step)

from PyQt5 import QtWidgets, QtCore, QtGui
import math

class WaveformVisualizer(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(20) # 50 FPS
        self.phase = 0
        self.amplitude = 10
        self.active = False
        
    def set_active(self, active):
        self.active = active
        self.amplitude = 40 if active else 5
        self.update()

    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)
        
        # Draw Background (Transparent)
        # painter.fillRect(self.rect(), QtGui.QColor(0, 0, 0, 0))
        
        width = self.width()
        height = self.height()
        mid_y = height / 2
        
        # Color: NOVA Cyan or Pulse Red depending on amplitude? Keep Cyan for now.
        color = QtGui.QColor("#00d4ff")
        color.setAlpha(200)
        pen = QtGui.QPen(color, 3)
        painter.setPen(pen)
        
        path = QtGui.QPainterPath()
        path.moveTo(0, mid_y)
        
        # Draw Sine Wave
        for x in range(0, width, 5):
            # Dynamic frequency and amplitude
            rel_x = x / width
            
            # Taper ends
            taper = 4 * rel_x * (1 - rel_x) 
            
            y = mid_y + self.amplitude * taper * math.sin(0.05 * x + self.phase)
            path.lineTo(x, y)
            
        painter.drawPath(path)
        
        self.phase += 0.2
        if self.phase > 2 * math.pi:
            self.phase -= 2 * math.pi

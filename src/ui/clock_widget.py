from PyQt6.QtWidgets import (QWidget, QHBoxLayout, QVBoxLayout, QLabel, 
                             QFrame)
from PyQt6.QtCore import QTimer, QTime, QDate, Qt
from PyQt6.QtGui import QFont

class ClockWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Main Layout (Vertical: Clock Row, Date Row)
        main_layout = QVBoxLayout(self)
        main_layout.setSpacing(5)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
        # --- Time Row ---
        time_layout = QHBoxLayout()
        time_layout.setSpacing(10)
        
        # Hour
        self.hour_panel = self._create_digit_panel("00", "H")
        self.hour_label = self.hour_panel.findChild(QLabel, "digit")
        
        # Minute
        self.min_panel = self._create_digit_panel("00", "M")
        self.min_label = self.min_panel.findChild(QLabel, "digit")
        
        # Second
        self.sec_panel = self._create_digit_panel("00", "S")
        self.sec_label = self.sec_panel.findChild(QLabel, "digit")
        
        self.ampm_label = QLabel("AM")
        self.ampm_label.setStyleSheet("color: white; font-size: 16px; font-weight: bold;")
        
        time_layout.addWidget(self.hour_panel)
        time_layout.addWidget(self.min_panel)
        time_layout.addWidget(self.sec_panel)
        time_layout.addWidget(self.ampm_label)
        
        main_layout.addLayout(time_layout)
        
        # Date Row
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.date_label.setStyleSheet("""
            color: #888888; 
            font-size: 14px;
            padding: 5px;
            background: transparent;
            border-top: 1px solid #222;
            margin-top: 5px;
        """)
        self.date_label.setFont(QFont("Arial", 12)) 
        
        main_layout.addWidget(self.date_label)
        
        # Timer
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000) # 1 sec
        
        self.update_time()

    def _create_digit_panel(self, text, suffix):
        panel = QFrame()
        panel.setStyleSheet("""
            QFrame {
                background-color: #252525;
                border: 1px solid #333;
                border-radius: 8px;
            }
        """)
        panel.setFixedSize(70, 70)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Space for PM/AM if needed (top)
        layout.addStretch()
        
        # Digit
        digit_lbl = QLabel(text)
        digit_lbl.setObjectName("digit")
        digit_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        digit_lbl.setStyleSheet("color: white; border: none;")
        digit_lbl.setFont(QFont("Arial", 32, QFont.Weight.Bold))
        layout.addWidget(digit_lbl)
        
        # Suffix (H, M, S)
        suffix_lbl = QLabel(suffix)
        suffix_lbl.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignBottom)
        suffix_lbl.setStyleSheet("color: #aaaaaa; font-size: 12px; padding-right: 5px; padding-bottom: 2px; border: none;")
        layout.addWidget(suffix_lbl)
        
        return panel

    def update_time(self):
        now = QTime.currentTime()
        date = QDate.currentDate()
        
        # Format 12h
        h = now.hour()
        ampm = "AM"
        if h >= 12:
            ampm = "PM"
            if h > 12: h -= 12
        if h == 0: h = 12
        
        self.hour_label.setText(f"{h:02d}")
        self.min_label.setText(f"{now.minute():02d}")
        self.sec_label.setText(f"{now.second():02d}")
        self.ampm_label.setText(ampm)
        
        # Date: Saturday, January 17, 2026
        self.date_label.setText(date.toString("dddd, MMMM d, yyyy"))

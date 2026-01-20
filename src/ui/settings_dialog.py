from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QLabel, 
                             QSpinBox, QComboBox, QDialogButtonBox,
                             QFormLayout, QPushButton, QCheckBox)

from PyQt6.QtCore import pyqtSignal

class SettingsDialog(QDialog):
    # Signal to request test speech: (voice_name)
    test_voice_signal = pyqtSignal(str)

    def __init__(self, parent=None, current_interval=50, current_voice="F1", always_on_top=True, language="Korean", ticker_mode=False):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.resize(300, 250)
        
        layout = QVBoxLayout(self)
        form_layout = QFormLayout()
        
        self.language_combo = QComboBox()
        self.language_combo.addItems(["Korean", "English", "Spanish", "Portuguese", "French"])
        self.language_combo.setCurrentText(language)

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 10000)
        self.interval_spin.setValue(current_interval)
        self.interval_spin.setSuffix(" USD")
        
        self.voice_combo = QComboBox()
        # Supertonic supported voices
        voices = ['F1', 'F2', 'F3', 'F4', 'F5', 'M1', 'M2', 'M3', 'M4', 'M5']
        self.voice_combo.addItems(voices)
        self.voice_combo.setCurrentText(current_voice)
        
        self.always_top_check = QCheckBox("Enabled")
        self.always_top_check.setChecked(always_on_top)
        
        self.ticker_mode_check = QCheckBox("Enabled")
        self.ticker_mode_check.setChecked(ticker_mode)
        
        form_layout.addRow("Language:", self.language_combo)
        form_layout.addRow("Notification Interval:", self.interval_spin)
        form_layout.addRow("TTS Voice:", self.voice_combo)
        form_layout.addRow("Always on Top:", self.always_top_check)
        form_layout.addRow("Ticker Mode:", self.ticker_mode_check)
        
        layout.addLayout(form_layout)
        
        # Test Button
        self.test_btn = QPushButton("Test Voice")
        self.test_btn.clicked.connect(self.on_test_clicked)
        layout.addWidget(self.test_btn)
        
        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | 
                                   QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def on_test_clicked(self):
        selected_voice = self.voice_combo.currentText()
        self.test_voice_signal.emit(selected_voice)

    def get_settings(self):
        return {
            "language": self.language_combo.currentText(),
            "interval": self.interval_spin.value(),
            "voice": self.voice_combo.currentText(),
            "always_on_top": self.always_top_check.isChecked(),
            "ticker_mode": self.ticker_mode_check.isChecked()
        }

from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
                             QPushButton, QFrame)
from PyQt6.QtCore import Qt, pyqtSlot
from PyQt6.QtGui import QFont

from core.price_monitor import PriceMonitor
from core.interval_logic import IntervalTracker
from services.tts_service import TTSService
from ui.settings_dialog import SettingsDialog
from utils.settings_manager import SettingsManager, LANG_CODE_MAP
from utils.korean_numbers import number_to_korean

from ui.clock_widget import ClockWidget

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Bitcoin Ticker")

        # Settings Manager (Persistent)
        self.settings_manager = SettingsManager()
        
        # Load saved settings
        self.current_voice = self.settings_manager.get("voice", "F1")
        self.current_language = self.settings_manager.get("language", "Korean")
        self.always_on_top = self.settings_manager.get("always_on_top", True)
        self.ticker_mode = self.settings_manager.get("ticker_mode", False)
        saved_interval = self.settings_manager.get("interval", 50)

        # Core Components
        self.price_monitor = PriceMonitor()
        self.interval_tracker = IntervalTracker(interval=float(saved_interval))
        self.tts_service = TTSService()
        
        # Connect TTS error signal
        self.tts_service.tts_error.connect(self.on_tts_error)
        
        # Window Flags & Attributes
        if self.always_on_top:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        else:
            self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Dragging state
        self.old_pos = None

        # UI Setup
        self.central_widget = QWidget()
        self.central_widget.setStyleSheet("""
            QWidget {
                background-color: #121212;
                border: 1px solid #444;
                border-radius: 12px;
            }
        """) 
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(6, 4, 6, 4)
        self.main_layout.setSpacing(2)

        # Content Container (for layout switching)
        self.content_container = QWidget()
        self.content_container.setStyleSheet("background: transparent; border: none;")
        self.main_layout.addWidget(self.content_container)
        
        # === CREATE WIDGETS (shared between layouts) ===
        self.clock_widget = ClockWidget()
        
        # Price Display
        self.price_label = QLabel("Waiting...")
        self.price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.price_label.setStyleSheet("color: #00E676; border: none;") 
        font = QFont("Consolas, monospace", 32, QFont.Weight.Bold)
        font.setStyleHint(QFont.StyleHint.Monospace)
        self.price_label.setFont(font)
        
        self.price_indicator = QLabel("")
        self.price_indicator.setFixedWidth(25)
        self.price_indicator.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.price_indicator.setStyleSheet("color: #00E676; border: none; font-size: 20px;")

        # Simple time label (for ticker mode)
        self.simple_time_label = QLabel("00:00:00 AM")
        self.simple_time_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.simple_time_label.setStyleSheet("color: #888; border: none; font-size: 14px;")
        font_time = QFont("Consolas, monospace", 14)
        self.simple_time_label.setFont(font_time)
        
        # Simple date label (for ticker mode)
        self.simple_date_label = QLabel("")
        self.simple_date_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.simple_date_label.setStyleSheet("color: #aaa; border: none; font-size: 14px;")
        
        # Hour tracking for hourly chime
        self.current_hour = None
        
        # Status Badge
        self.status_label = QLabel("Connecting...")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.setStyleSheet("""
            background-color: #222;
            color: #888;
            padding: 2px 8px;
            border-radius: 10px;
            font-size: 11px;
            border: 1px solid #333;
        """)
        
        # Mute Button
        self.is_muted = self.settings_manager.get("muted", False)
        self.mute_btn = QPushButton("🔇" if self.is_muted else "🔊")
        self.mute_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.mute_btn.setToolTip("Mute/Unmute TTS")
        self.mute_btn.setStyleSheet("""
            QPushButton {
                background-color: #222; 
                color: #888; 
                border: 1px solid #333;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: #2a2a2a; 
                color: #aaa;
            }
            QPushButton:pressed {
                background-color: #333;
                color: white;
            }
        """)
        self.mute_btn.clicked.connect(self.toggle_mute)
        
        # Settings Button
        self.settings_btn = QPushButton("⚙️")
        self.settings_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.settings_btn.setToolTip("Settings")
        self.settings_btn.setStyleSheet("""
            QPushButton {
                background-color: #222; 
                color: #888; 
                border: 1px solid #333;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: #2a2a2a; 
                color: #aaa;
            }
            QPushButton:pressed {
                background-color: #333;
                color: white;
            }
        """)
        self.settings_btn.clicked.connect(self.open_settings)
        
        # Inline close button (for horizontal mode)
        self.inline_close_btn = QPushButton("✕")
        self.inline_close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.inline_close_btn.setToolTip("Close")
        self.inline_close_btn.setStyleSheet("""
            QPushButton {
                background-color: #222; 
                color: #888; 
                border: 1px solid #333;
                border-radius: 12px;
                padding: 2px 8px;
                font-size: 12px;
            }
            QPushButton:hover { 
                background-color: #3a2a2a; 
                color: #FF8888;
            }
            QPushButton:pressed {
                background-color: #FF5252;
                color: white;
            }
        """)
        self.inline_close_btn.clicked.connect(self.close)
        
        # Apply layout (horizontal only)
        self.setup_layout()

        # Signal Connections
        self.price_monitor.price_updated.connect(self.on_price_update)
        self.price_monitor.connection_status.connect(self.on_connection_status)
        self.interval_tracker.interval_crossed.connect(self.on_interval_crossed)
        
        # Start Monitor
        self.price_monitor.start()

    def setup_layout(self):
        """Setup layout based on ticker_mode"""
        # Clear existing layout if any
        if self.content_container.layout():
            layout = self.content_container.layout()
            while layout.count():
                item = layout.takeAt(0)
                if item.widget():
                    item.widget().setParent(None)
                elif item.layout():
                    self._clear_layout(item.layout())
            QWidget().setLayout(layout)

        # Keep the 1s timer running in both modes (drives the hourly chime;
        # the time labels themselves are only visible in ticker mode)
        from PyQt6.QtCore import QTimer
        if not hasattr(self, 'ticker_timer'):
            self.ticker_timer = QTimer()
            self.ticker_timer.timeout.connect(self.update_simple_time)
        self.ticker_timer.start(1000)
        self.update_simple_time()

        if self.ticker_mode:
            # === TICKER MODE: Single line layout ===
            self.main_layout.setContentsMargins(10, 2, 10, 2)
            
            layout = QHBoxLayout(self.content_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            # Hide clock widget in ticker mode
            self.clock_widget.hide()
            
            # Adjust fonts for ticker mode (similar sizes)
            ticker_price_font = QFont("Consolas, monospace", 18, QFont.Weight.Bold)
            self.price_label.setFont(ticker_price_font)
            self.price_indicator.setStyleSheet("color: #00E676; border: none; font-size: 14px;")
            
            ticker_time_font = QFont("Consolas, monospace", 18)
            self.simple_time_label.setFont(ticker_time_font)
            self.simple_time_label.setStyleSheet("color: white; border: none;")
            
            
            # Price with indicator
            layout.addWidget(self.price_label)
            layout.addWidget(self.price_indicator)
            
            # Separator
            separator = QFrame()
            separator.setFixedWidth(1)
            separator.setStyleSheet("background-color: #444;")
            layout.addWidget(separator)
            
            # Time and Date (horizontal, side by side)
            layout.addWidget(self.simple_time_label)
            layout.addWidget(self.simple_date_label)
            
            # Separator between time and buttons
            separator2 = QFrame()
            separator2.setFixedWidth(1)
            separator2.setStyleSheet("background-color: #444;")
            layout.addWidget(separator2)
            
            # Buttons (no status label in ticker mode)
            layout.addWidget(self.mute_btn)
            layout.addWidget(self.settings_btn)
            layout.addWidget(self.inline_close_btn)
            
            self.resize(540, 45)  # Slightly wider for separator
            self.setFixedHeight(45)  # Force height adjustment

        else:
            # === NORMAL MODE: Clock + Price ===
            self.main_layout.setContentsMargins(6, 4, 6, 4)

            # Remove fixed height constraint for normal mode
            self.setMinimumHeight(0)
            self.setMaximumHeight(16777215)  # QWIDGETSIZE_MAX

            layout = QHBoxLayout(self.content_container)
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(10)
            
            # Restore original font for normal mode
            normal_price_font = QFont("Consolas, monospace", 32, QFont.Weight.Bold)
            self.price_label.setFont(normal_price_font)
            
            # Show clock widget
            self.clock_widget.show()
            self.clock_widget.date_label.show()
            self.clock_widget.date_label.setStyleSheet("""
                color: #888888; 
                font-size: 14px;
                padding: 2px;
                background: transparent;
                border: none;
            """)
            
            # Left: Clock (vertically centered)
            clock_zone = QVBoxLayout()
            clock_zone.addStretch()
            clock_zone.addWidget(self.clock_widget)
            clock_zone.addStretch()
            
            # Right: Price + Info (vertically centered)
            price_zone = QVBoxLayout()
            price_zone.setSpacing(3)
            price_zone.addStretch()
            
            # Price row
            price_row = QHBoxLayout()
            price_row.addStretch()
            price_row.addWidget(self.price_label)
            price_row.addWidget(self.price_indicator)
            price_row.addStretch()
            price_zone.addLayout(price_row)
            
            # Info row (with inline close button)
            info_row = QHBoxLayout()
            info_row.setSpacing(3)
            info_row.addStretch()
            info_row.addWidget(self.status_label)
            info_row.addWidget(self.mute_btn)
            info_row.addWidget(self.settings_btn)
            info_row.addWidget(self.inline_close_btn)
            info_row.addStretch()
            price_zone.addLayout(info_row)
            price_zone.addStretch()
            
            # Separator line between clock and price
            separator = QFrame()
            separator.setFixedWidth(1)
            separator.setStyleSheet("background-color: #444;")
            
            layout.addLayout(clock_zone)
            layout.addWidget(separator)
            layout.addLayout(price_zone)

            self.resize(520, 100)  # Normal size
    
    def update_simple_time(self):
        """Update simple time and date labels for ticker mode"""
        from datetime import datetime
        now = datetime.now()
        
        # Update time
        time_str = now.strftime("%I:%M:%S %p")
        self.simple_time_label.setText(time_str)
        
        # Update date (with day of week)
        date_str = now.strftime("%a, %b %d")
        self.simple_date_label.setText(date_str)
        
        # Hourly chime check
        current_hour = now.hour
        if self.current_hour is not None and current_hour != self.current_hour:
            # Hour changed - play chime
            self.play_hourly_chime()
        self.current_hour = current_hour
    
    def play_hourly_chime(self):
        """Play a simple beep sound for hourly notification"""
        try:
            import winsound
            # Play a short beep (frequency=1000Hz, duration=200ms)
            winsound.Beep(1000, 200)
        except Exception:
            # Fallback: use system bell
            print("\a")  # ASCII bell character

    def _clear_layout(self, layout):
        """Recursively clear a layout"""
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().setParent(None)
            elif item.layout():
                self._clear_layout(item.layout())

    # --- Frameless Window Dragging Logic ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event):
        if self.old_pos:
            delta = event.globalPosition().toPoint() - self.old_pos
            self.move(self.pos() + delta)
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = None

    @pyqtSlot(float)
    def on_price_update(self, price):
        # Get previous price for direction indicator
        prev_price = self.interval_tracker.last_price

        # Update price text (fixed position)
        self.price_label.setText(f"${price:,.2f}")

        # Update indicator separately (fixed width, no layout shift)
        if prev_price is not None:
            if price > prev_price:
                self.price_indicator.setText("▲")
                self.price_indicator.setStyleSheet("color: #00E676; border: none; font-size: 20px;")
            elif price < prev_price:
                self.price_indicator.setText("▼")
                self.price_indicator.setStyleSheet("color: #FF5252; border: none; font-size: 20px;")
            # else: keep previous indicator

        self.interval_tracker.process_price(price)

    @pyqtSlot(bool)
    def on_connection_status(self, connected):
        self.status_label.setText("Connected" if connected else "Disconnected")
        color = "#00E676" if connected else "#FF5252"
        self.status_label.setStyleSheet(f"""
            background-color: #222;
            color: {color};
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            border: 1px solid {color};
        """)

    @pyqtSlot(float, str)
    def on_interval_crossed(self, price, direction):
        # Use shared constant from settings_manager
        lang_code = LANG_CODE_MAP.get(self.current_language, "ko")

        price_int = int(price)
        text = ""
        
        if self.current_language == "Korean":
            # Convert number to Korean text for proper pronunciation
            price_korean = number_to_korean(price_int)
            text = f"{price_korean}달러를 돌파했습니다." if direction == "UP" else f"{price_korean}달러가 깨어졌습니다."
        elif self.current_language == "English":
            text = f"Bitcoin passed {price_int} dollars." if direction == "UP" else f"Bitcoin dropped below {price_int} dollars."
        elif self.current_language == "Spanish":
            text = f"Bitcoin superó los {price_int} dólares." if direction == "UP" else f"Bitcoin cayó por debajo de los {price_int} dólares."
        elif self.current_language == "Portuguese":
            text = f"O Bitcoin ultrapassou {price_int} dólares." if direction == "UP" else f"O Bitcoin caiu abaixo de {price_int} dólares."
        elif self.current_language == "French":
            text = f"Le Bitcoin a dépassé {price_int} dollars." if direction == "UP" else f"Le Bitcoin est tombé sous {price_int} dollars."
            
        print(f"Triggering TTS: {text} ({self.current_voice}, {lang_code})")
        
        # Skip TTS if muted
        if not self.is_muted:
            self.tts_service.speak(text, voice=self.current_voice, lang=lang_code)

    def open_settings(self):
        current_interval = int(self.interval_tracker.interval)
        
        dialog = SettingsDialog(self, current_interval, self.current_voice, self.always_on_top, self.current_language, self.ticker_mode)
        
        # Connect test signal
        dialog.test_voice_signal.connect(self.run_voice_test)
        
        if dialog.exec():
            settings = dialog.get_settings()
            new_interval = settings["interval"]
            self.current_voice = settings["voice"]
            new_always_top = settings["always_on_top"]
            self.current_language = settings["language"]
            new_ticker_mode = settings["ticker_mode"]
            
            # Update Interval
            self.interval_tracker.set_interval(float(new_interval))
            
            # Save settings persistently
            self.settings_manager.update({
                "interval": new_interval,
                "voice": self.current_voice,
                "language": self.current_language,
                "always_on_top": new_always_top,
                "ticker_mode": new_ticker_mode
            })
            
            # Update Ticker Mode if changed
            if new_ticker_mode != self.ticker_mode:
                self.ticker_mode = new_ticker_mode
                self.setup_layout()
            
            # Update Window Flags if changed
            if new_always_top != self.always_on_top:
                self.always_on_top = new_always_top
                current_flags = self.windowFlags()
                if self.always_on_top:
                    self.setWindowFlags(current_flags | Qt.WindowType.WindowStaysOnTopHint)
                else:
                    self.setWindowFlags(current_flags & ~Qt.WindowType.WindowStaysOnTopHint)
                self.show()

    def run_voice_test(self, voice):
        # Use shared constant
        lang_code = LANG_CODE_MAP.get(self.current_language, "ko")

        price = self.interval_tracker.last_price
        price_val = int(price) if price else 0
        text = ""
        
        if self.current_language == "Korean":
            if price:
                price_korean = number_to_korean(price_val)
                text = f"현재 비트코인 가격은 {price_korean}달러입니다."
            else:
                text = "비트코인 가격 정보를 기다리고 있어요"
        elif self.current_language == "English":
            text = f"Current Bitcoin price is {price_val} dollars." if price else "Waiting for Bitcoin price data."
        elif self.current_language == "Spanish":
            text = f"El precio actual de Bitcoin es {price_val} dólares." if price else "Esperando datos del precio de Bitcoin."
        elif self.current_language == "Portuguese":
            text = f"O preço atual do Bitcoin é {price_val} dólares." if price else "Aguardando dados de preço do Bitcoin."
        elif self.current_language == "French":
            text = f"Le prix actuel du Bitcoin est de {price_val} dollars." if price else "En attente des données sur le prix du Bitcoin."
            
        # Speak with cache=False
        self.tts_service.speak(text, voice=voice, lang=lang_code, cache=False)

    @pyqtSlot(str)
    def on_tts_error(self, error_message):
        """Handle TTS errors with UI feedback"""
        # Flash the status label briefly as error indicator
        self.status_label.setStyleSheet("""
            background-color: #222;
            color: #FF5252;
            padding: 2px 8px;
            border-radius: 12px;
            font-size: 11px;
            border: 1px solid #FF5252;
        """)
        self.status_label.setText("TTS Error")
        print(f"[UI] TTS Error: {error_message}")

    def toggle_mute(self):
        """Toggle mute state for TTS"""
        self.is_muted = not self.is_muted
        
        # Update button icon
        self.mute_btn.setText("🔇" if self.is_muted else "🔊")
        
        # Save to settings
        self.settings_manager.set("muted", self.is_muted)
        
        print(f"TTS Muted: {self.is_muted}")

    def closeEvent(self, event):
        self.price_monitor.stop()
        super().closeEvent(event)

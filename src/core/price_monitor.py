import json
import threading
import time
import websocket
from PyQt6.QtCore import QObject, pyqtSignal

class PriceMonitor(QObject):
    price_updated = pyqtSignal(float)
    connection_status = pyqtSignal(bool)

    def __init__(self, symbol="btcusdt"):
        super().__init__()
        self.symbol = symbol.lower()
        # Use Binance Global as it's often more reliable for international users
        # Was: wss://stream.binance.us:9443/ws/...
        self.ws_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@trade"
        self.ws = None
        self.keep_running = True
        self.thread = None

    def start(self):
        self.keep_running = True
        self.thread = threading.Thread(target=self._run_ws, daemon=True)
        self.thread.start()

    def stop(self):
        self.keep_running = False
        if self.ws:
            self.ws.close()
        if self.thread:
            self.thread.join(timeout=1.0)

    def _run_ws(self):
        while self.keep_running:
            try:
                self.connection_status.emit(False)
                print(f"Connecting to {self.ws_url}...")
                self.ws = websocket.WebSocketApp(
                    self.ws_url,
                    on_open=self._on_open,
                    on_message=self._on_message,
                    on_error=self._on_error,
                    on_close=self._on_close
                )
                
                # Standard run without bypassing SSL
                self.ws.run_forever(ping_interval=60, ping_timeout=10)
                
                if self.keep_running:
                    print("WS Reconnecting in 5s...")
                    time.sleep(5) # Reconnect delay
            except Exception as e:
                print(f"WS Critical Error: {e}")
                time.sleep(5)

    def _on_open(self, ws):
        print("WebSocket Connected")
        self.connection_status.emit(True)

    def _on_message(self, ws, message):
        try:
            data = json.loads(message)
            # Check if this is a trade message
            if 'p' in data:
                price = float(data['p'])
                self.price_updated.emit(price)
            else:
                # Ping/Pong or other messages
                pass
        except Exception as e:
            print(f"Parse Error: {e}")

    def _on_error(self, ws, error):
        print(f"WebSocket Error: {error}")

    def _on_close(self, ws, close_status_code, close_msg):
        print(f"WebSocket Closed: {close_status_code} - {close_msg}")
        self.connection_status.emit(False)

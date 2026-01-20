import websocket
import threading
import time

def on_message(ws, message):
    print(f"Received: {message}")

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print(f"Closed: {close_status_code} - {close_msg}")

def on_open(ws):
    print("Opened connection")

if __name__ == "__main__":
    # symbol = "btcusdt"
    # url = f"wss://stream.binance.us:9443/ws/{symbol}@trade"
    # Testing both US and Global to see which works
    
    urls = [
        "wss://stream.binance.us:9443/ws/btcusdt@trade",
        "wss://stream.binance.com:9443/ws/btcusdt@trade"
    ]
    
    for url in urls:
        print(f"Testing URL: {url}")
        ws = websocket.WebSocketApp(url,
                                  on_open=on_open,
                                  on_message=on_message,
                                  on_error=on_error,
                                  on_close=on_close)
        
        # Run for 5 seconds
        t = threading.Thread(target=ws.run_forever)
        t.start()
        time.sleep(5)
        ws.close()
        t.join()
        print("-" * 20)

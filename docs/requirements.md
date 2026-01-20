# Bitcoin Ticker Requirements

## Core Features

### 1. Bitcoin Price Monitoring
- Real-time price updates via Binance WebSocket API (`wss://stream.binance.com:9443/ws/btcusdt@trade`)
- Robust connection handling with auto-reconnect
- Price change indicator (▲/▼) with color coding

### 2. Text-to-Speech (TTS) Notifications
- **Engine**: Supertonic AI (via direct ONNX inference)
- **Languages**: Korean, English, Spanish, Portuguese, French
- **Voices**: 10 selectable voices (F1-F5, M1-M5)
- **Trigger**: User-defined price intervals (e.g., every $50 change)
- **Korean Number Conversion**: Proper pronunciation (e.g., 95500 → "구만 오천오백")
- **Mute Toggle**: 🔊/🔇 button to silence TTS notifications
- **Caching**: Local caching of generated audio to minimize latency
- **Error Handling**: Visual feedback on TTS failures
- **Offline Support**: Uses locally downloaded models and assets

### 3. User Interface (UI)
- **Style**: Modern, High-Contrast Dark Theme
- **Window**: 
  - Frameless design with rounded corners
  - Draggable anywhere
  - "Always on Top" toggle
  - DPI scaling support (Windows)
- **Layout**: Horizontal (520×110px)
  - Clock zone (left) with separator
  - Price zone (right)
- **Components**:
  - **Flip Clock**: Digital clock with AM/PM and Date display
  - **Price Display**: Large green price with change indicator
  - **Status Badge**: Connection status
  - **Mute Button**: Toggle TTS on/off
  - **Settings Button**: Open settings dialog
  - **Close Button**: Inline close button

### 4. Settings
- **Interval Control**: Adjust notification triggers ($10, $50, $100, etc.)
- **Voice Selection**: Choose from 10 Supertonic voices
- **Language Selection**: 5 supported languages
- **Always on Top**: Toggle window behavior
- **Persistence**: Settings saved to `settings.json`
- **Testing**: "Test Voice" button to preview TTS settings

## Technical Stack
- **Language**: Python 3.10+
- **GUI Framework**: PyQt6
- **TTS Engine**: Custom ONNX Runtime implementation (Supertonic weights)
- **Audio Playback**: PyQt6 QMediaPlayer
- **Data Source**: websocket-client (Binance WebSocket)
- **Settings Storage**: JSON file

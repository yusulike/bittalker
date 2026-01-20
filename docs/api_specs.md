# API Specifications

## 1. Price Data Source (Binance US WebSocket)
*Using Binance US for stable USD pairs.*

- **Endpoint**: `wss://stream.binance.us:9443/ws/btcusdt@trade`
- **Protocol**: WebSocket
- **Response Format**:
  ```json
  {
    "e": "trade",     // Event type
    "E": 123456789,   // Event time
    "s": "BTCUSDT",   // Symbol
    "t": 12345,       // Trade ID
    "p": "9450.01",   // Price
    "q": "0.100",     // Quantity
    "T": 123456785,   // Trade time
    "m": true,        // Is the buyer the market maker?
    "M": true         // Ignore
  }
  ```

## 2. Text-to-Speech (Supertonic)
*Integration via `supertonic` Python package or REST API.*

### Option A: Local Python Package (`supertonic`)
- **Installation**: `pip install supertonic` (Requires ONNX Runtime)
- **Supported Languages**: `en` (English), `ko` (Korean), `es` (Spanish), `pt` (Portuguese), `fr` (French)
- **Official API Usage (per README)**:
  ```python
  from supertonic import TTS
  
  engine = TTS(auto_download=True)
  
  # Basic Synthesis
  # Note: 1.0.0 package may require patching for non-English languages
  text = "안녕하세요"
  # engine.synthesize(text, lang='ko') # Ideal Usage per specs
  ```

- **Arguments (Inference)**:
    - `text`: Input text.
    - `voice_style`: Path to voice style JSON or Style object.
    - `speed`: Playback speed (default 1.05).
    - `total_step`: Denoising steps (default 5, higher=better quality).
    - `lang`: Language code (important for non-English).

- **Available Voices**: `F1`~`F5`, `M1`~`M5`.

### Option B: Supertone Cloud API
- **Endpoint**: `https://api.supertone.ai/v1/synthesize` (Hypothetical)
- **Headers**:
    - `Authorization`: `Bearer <API_KEY>`
    - `Content-Type`: `application/json`
- **Body**:
  ```json
  {
    "text": "9450달러를 돌파했습니다",
    "voice_id": "ko_kr_female_1",
    "speed": 1.0
  }
  ```

*Note: Implementation will default to checking for the local package or asking for API keys if cloud is preferred.*

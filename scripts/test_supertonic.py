try:
    from supertonic import TTS
    print("Initializing TTS...")
    engine = TTS(auto_download=True)
    print("TTS initialized.")
    print(f"Methods: {[m for m in dir(engine) if not m.startswith('_')]}")

except Exception as e:
    print(f"Error: {e}")

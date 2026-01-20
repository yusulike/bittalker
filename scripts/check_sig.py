try:
    from supertonic import TTS
    import inspect
    
    print("Checking synthesize signature...")
    sig = inspect.signature(TTS.synthesize)
    print(f"Synthesize signature: {sig}")
    
except Exception as e:
    print(f"Error: {e}")

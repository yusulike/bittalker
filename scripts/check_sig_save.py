try:
    from supertonic import TTS
    import inspect
    
    print("Checking save_audio signature...")
    sig = inspect.signature(TTS.save_audio)
    print(f"save_audio signature: {sig}")
    
except Exception as e:
    print(f"Error: {e}")

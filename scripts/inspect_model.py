try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    
    print(f"Model object: {engine.model}")
    print(f"Model dir: {dir(engine.model)}")
    
    # Check if model is callable
    if callable(engine.model):
        print("Model is callable")
        import inspect
        try:
             print(f"Model call sig: {inspect.signature(engine.model.__call__)}")
        except:
             print("Could not get signature of model.__call__")

except Exception as e:
    print(f"Error: {e}")

try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    
    func = engine.model.__call__
    print(f"Func: {func}")
    # print(f"Varnames: {func.__code__.co_varnames}") # Might fail if it's a bound method wrapper?
    # Actually if it's a method of Supertonic class instance.
    
    import inspect
    sig = inspect.signature(func)
    print(f"Signature: {sig}")
    
    # Check param names
    print("Params:", list(sig.parameters.keys()))

except Exception as e:
    print(f"Error: {e}")

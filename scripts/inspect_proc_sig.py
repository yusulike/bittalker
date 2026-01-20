try:
    from supertonic import TTS
    import inspect
    engine = TTS(auto_download=True)
    proc = engine.model.text_processor
    
    print(f"Processor call sig: {inspect.signature(proc.__call__)}")
    
    # Check if indexer is list or dict
    print(f"Indexer type: {type(proc.indexer)}")

except Exception as e:
    print(f"Error: {e}")

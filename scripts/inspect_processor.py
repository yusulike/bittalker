try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    model = engine.model
    
    print(f"Batch method? {'batch' in dir(model)}")
    if hasattr(model, 'batch'):
        import inspect
        print(f"Batch sig: {inspect.signature(model.batch)}")
        
    print(f"Text processor: {model.text_processor}")
    print(f"Processor dir: {dir(model.text_processor)}")
    
    # Check if we can see supported languages
    if hasattr(model.text_processor, 'clean_text'):
        print("Has clean_text method")
        # clean_text sig?
    
except Exception as e:
    print(f"Error: {e}")

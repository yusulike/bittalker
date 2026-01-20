try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    indexer = engine.model.text_processor.indexer
    
    # Check for a Korean char
    # '가' is unicode 44032 (0xAC00)
    # The indexer keys are usually integers (ord(char))?
    # helper.py says: [self.indexer[val] for val in unicode_values]
    # keys are likely string repr of integers? or just integers?
    # helper.py: indexer = json.load(f) -> keys on JSON are always strings.
    
    korean_code = str(ord('가'))
    print(f"Checking for '가' ({korean_code}) in indexer...")
    if korean_code in indexer:
        print("Found '가'")
    else:
        print("NOT Found '가'")
        
    print(f"Indexer size: {len(indexer)}")
    
    # Check for <ko> tag
    # The helper.py says `text = f"<{lang}>" + text ...`
    # and unicode_values calls ord(char).
    # so < is 60, k is 107, o is 111, > is 62.
    # The ONNX model receives sequence of IDs.
    # Wait, the TAG itself might be tokenized char by char?
    # helper.py text_preprocess adds the tag string.
    # `_text_to_unicode_values` converts string to array of uint16.
    # `[self.indexer[val] for val in unicode_values]`
    
    # So the model doesn't see "<ko>" as a special token, but as sequence of chars <, k, o, >?
    # OR the indexer maps `ord('<')` to some ID.
    
    print(f"Checking for '<' ({ord('<')}) in indexer...")
    if str(ord('<')) in indexer:
        print("Found '<'")
    else:
        print("NOT Found '<'")

except Exception as e:
    print(f"Error: {e}")

import numpy as np
try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    
    # Original processor
    original_proc = engine.model.text_processor
    indexer = original_proc.indexer
    
    class CustomProcessor:
        def __init__(self, indexer):
            self.indexer = indexer
            
        def validate_text(self, text):
            # Bypass validation or implement lenient one
            return True, []

        def __call__(self, text_list):
            lang = "ko"
            processed_list = []
            for t in text_list:
                # Basic cleanup could be done here
                # Wrap
                wrapped = f"<{lang}>{t}</{lang}>"
                processed_list.append(wrapped)
            
            # IDs
            lengths = [len(t) for t in processed_list]
            max_len = max(lengths)
            
            text_ids = np.zeros((len(processed_list), max_len), dtype=np.int64)
            
            for i, text in enumerate(processed_list):
                unicode_vals = [ord(c) for c in text]
                # Map using indexer
                # Assuming indexer is list where list[ord_val] = model_id
                ids = []
                for v in unicode_vals:
                    if v < len(self.indexer):
                         ids.append(self.indexer[v])
                    else:
                         ids.append(0) # UNK?
                
                text_ids[i, :len(ids)] = np.array(ids, dtype=np.int64)
            
            # Mask
            text_ids_lengths = np.array(lengths, dtype=np.int64)
            # Reimplement length_to_mask logic
            # tensor shape [B, 1, T] usually?
            # Model expectation: Name: text_mask, Type: tensor(float), Shape: ['batch_size', 1, 'text_length']
            
            mask = np.arange(max_len)[None, :] < text_ids_lengths[:, None]
            mask = mask.astype(np.float32)
            mask = mask[:, None, :] # Add channel dim? Inspect onnx said: ['batch_size', 1, 'text_length']
            
            return text_ids, mask

    # Verify mask shape matches what inspect_onnx said: ['batch_size', 1, 'text_length']
    
    # Apply patch
    engine.model.text_processor = CustomProcessor(indexer)
    
    # Test Synthesis
    text = "안녕하세요"
    voice = "F1"
    style = engine.get_voice_style(voice)
    
    print(f"Synthesizing: {text}")
    # The wrapper calls model(text, style...) which calls text_processor([text])
    # The installed model.__call__ handles calling processor.
    # Wait, signature of installed model.__call__ was (text_list, style, ...)
    
    # engine.synthesize calls engine.model([text], style...)
    
    audio_tuple = engine.synthesize(text, voice_style=style)
    wav = audio_tuple[0]
    
    print(f"Success! Wav shape: {wav.shape}")
    
    import soundfile as sf
    sf.write("test_monkey_ko.wav", wav, 24000) # Assuming 24k

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

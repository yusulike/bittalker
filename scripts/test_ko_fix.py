try:
    from supertonic import TTS
    import soundfile as sf
    import os
    
    print("Initializing TTS...")
    engine = TTS(auto_download=True)
    
    text = "안녕하세요 비트코인입니다"
    voice = "F1"
    
    # Get style
    # TTS wrapper usually handles this. engine.get_voice_style returns what?
    style = engine.get_voice_style(voice)
    print(f"Style type: {type(style)}")
    
    # Direct call to model
    # Signature: (text, lang, style, total_step, speed)
    print(f"Synthesizing: {text} (lang='ko')")
    
    wav, duration = engine.model(text, "ko", style)
    
    print(f"Success! Wav shape: {wav.shape}, Duration: {duration}")
    
    # Save manually
    output_path = "test_ko_result.wav"
    sr = engine.model.sample_rate # Assuming it exists, implied by example code
    sf.write(output_path, wav, sr)
    print(f"Saved to {output_path}")

except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

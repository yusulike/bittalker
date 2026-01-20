try:
    from supertonic import TTS
    engine = TTS(auto_download=True)
    model = engine.model
    
    print("Inspecting Text Encoder inputs...")
    inputs = model.text_enc_ort.get_inputs()
    for inp in inputs:
        print(f"Name: {inp.name}, Type: {inp.type}, Shape: {inp.shape}")

except Exception as e:
    print(f"Error: {e}")

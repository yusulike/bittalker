try:
    from supertonic import TTS
    print("Initializing TTS...")
    engine = TTS(auto_download=True)
    
    text = "안녕하세요 비트코인입니다"
    voice = engine.voice_style_names[0]
    style = engine.get_voice_style(voice)
    
    print(f"Synthesizing: {text}")
    try:
        # Try passing language='ko' (common guess)
        engine.synthesize(text, voice_style=style, language='ko')
        print("Success with language='ko'")
    except TypeError:
        print("synthesize() does not accept 'language' arg. Trying 'lang'...")
        try:
             engine.synthesize(text, voice_style=style, lang='ko')
             print("Success with lang='ko'")
        except Exception as e:
            print(f"Failed with lang='ko': {e}")
            
            # Try inspection of the method logic or defaults
            print("Inspecting synthesize arguments again...")
            import inspect
            print(inspect.signature(engine.synthesize))

    except Exception as e:
        print(f"Error with language='ko': {e}")

except Exception as e:
    print(f"Fatal: {e}")

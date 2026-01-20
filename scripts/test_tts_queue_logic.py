
import sys
import os
import time
import threading
from unittest.mock import MagicMock

# Add src to sys.path
sys.path.append(os.path.join(os.getcwd(), 'src'))

# Mock PyQt6
from PyQt6.QtCore import QCoreApplication

# We need to mock winsound before importing tts_service if it was used at module level, 
# but tts_service imports it inside methods or at top level.
# We will patch it after import.

from services.tts_service import TTSService
import winsound

# Patch winsound
original_playsound = winsound.PlaySound

def mock_playsound(filepath, flags):
    # Simulate playing duration
    # We'll use the filename to determine duration if needed, or just fixed
    print(f"[{time.strftime('%H:%M:%S')}] MOCK AUDIO START: {filepath}")
    time.sleep(1.0) # 1 second duration
    print(f"[{time.strftime('%H:%M:%S')}] MOCK AUDIO END: {filepath}")

winsound.PlaySound = mock_playsound
winsound.SND_FILENAME = 0
winsound.SND_ASYNC = 1

def run_test():
    # Needed for QObject
    app = QCoreApplication([])
    
    # Initialize Service
    # Note: TTSService init tries to load ONNX models. 
    # We should mock _scan_voice_styles and load_text_to_speech to be faster and not require files.
    
    # We'll patch TTSService internal methods to bypass model loading
    TTSService._scan_voice_styles = MagicMock(return_value=["F1"])
    
    # We need to suppress the actual model loading in __init__ or just let it fail/print?
    # __init__ calls helper.load_text_to_speech. We should mock that.
    # It imports from services.helper.
    
    import services.tts_service
    services.tts_service.load_text_to_speech = MagicMock(return_value=MagicMock())
    services.tts_service.load_voice_style = MagicMock(return_value={})
    
    service = TTSService()
    
    # Also mock _generate_audio to just return success without doing anything
    # It writes to a file. We'll just touch the file so _play_audio finds it.
    def mock_generate(text, voice, lang, output_path):
        with open(output_path, 'w') as f:
            f.write("dummy")
        return
        
    service._generate_audio = MagicMock(side_effect=mock_generate)
    
    print("--- Testing TTS Queue Logic ---")
    
    # 1. Start First Message
    print(f"[{time.strftime('%H:%M:%S')}] Requesting Msg 1")
    service.speak("Msg 1", cache=True)
    
    time.sleep(0.2)
    
    # 2. Start Second Message (Should be queued)
    print(f"[{time.strftime('%H:%M:%S')}] Requesting Msg 2 (Should queue)")
    service.speak("Msg 2", cache=True)
    
    time.sleep(0.2)
    
    # 3. Start Third Message (Should override Msg 2)
    print(f"[{time.strftime('%H:%M:%S')}] Requesting Msg 3 (Should override Msg 2)")
    service.speak("Msg 3", cache=True)
    
    # Wait for completion
    # Msg 1 takes 1s. Ends at T+1.0
    # Then Msg 3 should start. Ends at T+2.0.
    # Msg 2 should never play.
    
    time.sleep(3.0)
    print("--- Test Finished ---")

if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Test Error: {e}")
        import traceback
        traceback.print_exc()

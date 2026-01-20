import os
import hashlib
import threading
import time
import winsound
import numpy as np
import soundfile as sf # Required for helper.py style saving
from PyQt6.QtCore import QObject, pyqtSignal, QUrl

# Import from the user-provided helper.py
# Assuming src/services/helper.py exists and path includes src/
from services.helper import load_text_to_speech, load_voice_style, sanitize_filename

class TTSService(QObject):
    # Signal emitted when TTS generation fails
    tts_error = pyqtSignal(str)  # error message
    
    def __init__(self, cache_dir="cache"):
        super().__init__()
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
        self.engine = None
        self.voice_styles_map = {} # Cache loaded voice styles
        self.available_voice_names = []
        
        try:
            # Assets path
            self.assets_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'assets'))
            self.onnx_dir = os.path.join(self.assets_path, "onnx")
            self.voice_styles_dir = os.path.join(self.assets_path, "voice_styles")
            
            print(f"Loading Supertonic TTS from: {self.assets_path}")
            
            if os.path.exists(self.onnx_dir) and os.path.exists(self.voice_styles_dir):
                # Load Engine
                # Using load_text_to_speech from helper.py
                self.engine = load_text_to_speech(self.onnx_dir, use_gpu=False)
                
                # Scan available voices
                self.available_voice_names = self._scan_voice_styles(self.voice_styles_dir)
                print(f"Supertonic TTS initialized via helper. Voices: {self.available_voice_names}")
            else:
                print(f"Assets not found at {self.assets_path}. Please download assets first.")
                self.engine = None
                 
        except Exception as e:
            print(f"Failed to init Supertonic via helper: {e}")
            self.engine = None

        # Queue system: size 1 with override structure
        self._is_playing = False
        self._play_lock = threading.Lock()
        self._pending_audio = None  # Tuple: (filepath,) or None

    def _scan_voice_styles(self, voice_dir):
        # Scan json files in voice_styles dir
        import glob
        files = glob.glob(os.path.join(voice_dir, "*.json"))
        names = [os.path.splitext(os.path.basename(f))[0] for f in files]
        return sorted(names)

    def speak(self, text, voice="F1", lang="ko", cache=True):
        """
        Generates audio.
        If cache=True: checks/saves to cache.
        If cache=False: generates to temp file, plays, doesn't persist.
        """
        threading.Thread(target=self._process_speech, args=(text, voice, lang, cache), daemon=True).start()

    def _process_speech(self, text, voice, lang, cache):
        if cache:
            filename = self._get_cache_filename(text, voice, lang)
            filepath = os.path.join(self.cache_dir, filename)
        else:
            filepath = os.path.join(self.cache_dir, "temp_test_voice.wav")

        if not cache or not os.path.exists(filepath):
            print(f"Generating TTS (Cache={cache}, Lang={lang}) for: {text}")
            self._generate_audio(text, voice, lang, filepath)
        
        if os.path.exists(filepath):
            self._play_audio(filepath)

    def _get_cache_filename(self, text, voice, lang):
        key = f"{text}_{voice}_{lang}".encode('utf-8')
        hash_digest = hashlib.md5(key).hexdigest()
        return f"{hash_digest}.wav"

    def _generate_audio(self, text, voice, lang, output_path):
        success = False
        if self.engine:
            try:
                # Resolve voice
                voice_name = voice
                if self.available_voice_names and voice_name not in self.available_voice_names:
                    voice_name = self.available_voice_names[0]
                    print(f"Requested voice '{voice}' not found. Using '{voice_name}'.")
                
                # Load Voice Style using helper.py
                # Check cache first
                if voice_name not in self.voice_styles_map:
                    voice_path = os.path.join(self.voice_styles_dir, f"{voice_name}.json")
                    style = load_voice_style([voice_path], verbose=False)
                    self.voice_styles_map[voice_name] = style
                
                style = self.voice_styles_map[voice_name]

                # Synthesize
                # engine(text, lang, style, total_step, speed) -> returns (wav, duration)
                
                wav, duration = self.engine(
                    text=text,
                    lang=lang, 
                    style=style,
                    total_step=5,
                    speed=1.05
                )
                
                # Save Audio
                # Helper synthesis returns wav of shape [1, samples]
                # We need sample rate from engine
                sr = self.engine.sample_rate
                
                # Use soundfile to save (as in helper usage example)
                # wav[0, :int(sr * duration)] if purely from example, but __call__ returns full concatenated wav
                # TextToSpeech.__call__ returns wav_cat, dur_cat
                # wav_cat is [1, T]
                
                w = wav.squeeze() # Remove batch dim -> [T]
                sf.write(output_path, w, sr)
                
                success = True
            except Exception as e:
                error_msg = f"TTS Generation Error: {e}"
                print(error_msg)
                import traceback
                traceback.print_exc()
                self.tts_error.emit(error_msg)

        if not success:
            print(f"[Simulated or Failed Supertonic] Generating dummy for: {text}")
            self._create_dummy_wav(output_path)
            self.tts_error.emit("TTS failed, using fallback audio")

    def _create_dummy_wav(self, path):
        import wave
        import struct
        import math
        with wave.open(path, 'w') as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(44100)
            duration = 0.5
            data = []
            for i in range(int(duration * 44100)):
                value = int(32767.0 * math.sin(2.0 * math.pi * 440.0 * i / 44100.0))
                data.append(struct.pack('<h', value))
            wav_file.writeframes(b''.join(data))

    def _play_audio(self, filepath):
        """
        Queue-aware audio playback.
        If already playing, add to pending queue (size 1, override).
        """
        with self._play_lock:
            if self._is_playing:
                # Override existing pending audio
                self._pending_audio = (filepath,)
                print(f"[TTS Queue] Audio queued (override): {filepath}")
                return
            else:
                self._is_playing = True
        
        # Start playback in separate thread to allow sync wait
        threading.Thread(target=self._play_and_process_queue, args=(filepath,), daemon=True).start()
    
    def _play_and_process_queue(self, filepath):
        """
        Play audio synchronously, then process pending queue.
        """
        try:
            print(f"[TTS] Playing: {filepath}")
            # Use sync playback to know when it finishes
            winsound.PlaySound(filepath, winsound.SND_FILENAME)
        except Exception as e:
            print(f"Playback Error: {e}")
        
        # Check for pending audio
        with self._play_lock:
            if self._pending_audio:
                next_audio = self._pending_audio
                self._pending_audio = None
            else:
                self._is_playing = False
                next_audio = None
        
        # Play next audio if exists
        if next_audio:
            next_filepath = next_audio[0]
            print(f"[TTS Queue] Playing pending: {next_filepath}")
            self._play_and_process_queue(next_filepath)


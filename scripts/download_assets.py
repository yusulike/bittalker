import os
import shutil
from pathlib import Path
from huggingface_hub import snapshot_download

# Configuration
REPO_ID = "Supertone/supertonic-2"
REVISION = "main" # Assuming main branch for 2.0
ASSETS_DIR = Path("e:/myWork/bittalker/assets")

def download_assets():
    print(f"Downloading assets from {REPO_ID} (rev: {REVISION}) to {ASSETS_DIR}...")
    
    # We download to a temp location first or directly?
    # snapshot_download can download to local_dir.
    
    try:
        snapshot_download(
            repo_id=REPO_ID, 
            local_dir=str(ASSETS_DIR), 
            revision=REVISION
        )
        print("Download complete.")
        
        # Verify
        expected_files = [
            "onnx/tts.json",
            "onnx/duration_predictor.onnx",
            "voice_styles/M1.json"
        ]
        for f in expected_files:
            p = ASSETS_DIR / f
            if p.exists():
                print(f"Verified: {f} exists")
            else:
                print(f"Warning: {f} MISSING")

    except Exception as e:
        print(f"Download failed: {e}")

if __name__ == "__main__":
    download_assets()

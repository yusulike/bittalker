import sys
import os
import ctypes

# === Windows DPI Handling ===
# Set process as DPI unaware to prevent OS-level scaling
if sys.platform == "win32":
    try:
        # PROCESS_DPI_UNAWARE = 0
        ctypes.windll.shcore.SetProcessDpiAwareness(0)
    except Exception:
        pass

# Disable Qt's own scaling
os.environ["QT_SCALE_FACTOR"] = "1"
os.environ["QT_AUTO_SCREEN_SCALE_FACTOR"] = "0"
os.environ["QT_SCREEN_SCALE_FACTORS"] = "1"

# Add src to python path to handle imports
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(current_dir)

from PyQt6.QtWidgets import QApplication
from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()

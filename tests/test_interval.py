import sys
import os
import unittest

# Add src to python path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(os.path.dirname(current_dir), 'src')
sys.path.append(src_dir)

from core.interval_logic import IntervalTracker

class TestIntervalLogic(unittest.TestCase):
    def setUp(self):
        self.tracker = IntervalTracker(interval=50.0)
        self.events = []
        self.tracker.interval_crossed.connect(lambda p, d: self.events.append((p, d)))

    def test_cross_up(self):
        self.tracker.process_price(9440) # Init
        self.tracker.process_price(9455) # Cross 9450
        
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0], (9450.0, "UP"))

    def test_cross_down(self):
        self.tracker.process_price(9460) # Init
        self.tracker.process_price(9440) # Cross 9450
        
        self.assertEqual(len(self.events), 1)
        self.assertEqual(self.events[0], (9450.0, "DOWN"))

    def test_multiple_cross(self):
        self.tracker.process_price(9400) # Init
        self.tracker.process_price(9510) # Cross 9450, 9500
        
        self.assertEqual(len(self.events), 2)
        self.assertEqual(self.events[0], (9450.0, "UP"))
        self.assertEqual(self.events[1], (9500.0, "UP"))

if __name__ == '__main__':
    # Initializing QApplication is needed for Signals to work? 
    # Actually pyqtSignal usually needs a QObject living in a QThread or just QCoreApplication. 
    # But for simple unit tests checking logic, it often works or needs minimal setup.
    # Let's import QCoreApplication just in case.
    from PyQt6.QtCore import QCoreApplication
    app = QCoreApplication(sys.argv)
    
    unittest.main()

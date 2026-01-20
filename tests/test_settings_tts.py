"""
TTS Service Tests
"""
import os
import sys
import unittest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.tts_service import TTSService
from utils.settings_manager import SettingsManager, LANG_CODE_MAP, DEFAULT_SETTINGS


class TestSettingsManager(unittest.TestCase):
    """Test the SettingsManager class"""
    
    def setUp(self):
        # Use a temporary test file
        self.test_file = "test_settings_temp.json"
        self.manager = SettingsManager(self.test_file)
    
    def tearDown(self):
        # Clean up test file
        if os.path.exists(self.manager.settings_file):
            os.remove(self.manager.settings_file)
    
    def test_default_settings(self):
        """Test that default settings are loaded correctly"""
        self.assertEqual(self.manager.get("interval"), 50)
        self.assertEqual(self.manager.get("voice"), "F1")
        self.assertEqual(self.manager.get("language"), "Korean")
        self.assertEqual(self.manager.get("always_on_top"), True)
    
    def test_set_and_get(self):
        """Test setting and getting values"""
        self.manager.set("interval", 100)
        self.assertEqual(self.manager.get("interval"), 100)
    
    def test_update_multiple(self):
        """Test updating multiple settings at once"""
        self.manager.update({
            "interval": 200,
            "voice": "M1"
        })
        self.assertEqual(self.manager.get("interval"), 200)
        self.assertEqual(self.manager.get("voice"), "M1")
    
    def test_persistence(self):
        """Test that settings persist across instances"""
        self.manager.set("language", "French")
        
        # Create a new manager instance with the same file
        new_manager = SettingsManager(self.test_file)
        self.assertEqual(new_manager.get("language"), "French")


class TestLangCodeMap(unittest.TestCase):
    """Test language code mapping"""
    
    def test_all_languages_mapped(self):
        """Test that all expected languages are in the map"""
        expected = ["Korean", "English", "Spanish", "Portuguese", "French"]
        for lang in expected:
            self.assertIn(lang, LANG_CODE_MAP)
    
    def test_correct_codes(self):
        """Test that language codes are correct"""
        self.assertEqual(LANG_CODE_MAP["Korean"], "ko")
        self.assertEqual(LANG_CODE_MAP["English"], "en")
        self.assertEqual(LANG_CODE_MAP["Spanish"], "es")
        self.assertEqual(LANG_CODE_MAP["Portuguese"], "pt")
        self.assertEqual(LANG_CODE_MAP["French"], "fr")


class TestTTSService(unittest.TestCase):
    """Test the TTS service"""
    
    def test_cache_filename_uniqueness(self):
        """Test that different inputs produce different cache filenames"""
        service = TTSService()
        
        file1 = service._get_cache_filename("Hello", "F1", "en")
        file2 = service._get_cache_filename("Hello", "F1", "ko")
        file3 = service._get_cache_filename("Hello", "M1", "en")
        file4 = service._get_cache_filename("Goodbye", "F1", "en")
        
        # All should be unique
        filenames = [file1, file2, file3, file4]
        self.assertEqual(len(filenames), len(set(filenames)))
    
    def test_cache_filename_deterministic(self):
        """Test that same inputs produce same cache filename"""
        service = TTSService()
        
        file1 = service._get_cache_filename("Test", "F1", "ko")
        file2 = service._get_cache_filename("Test", "F1", "ko")
        
        self.assertEqual(file1, file2)


if __name__ == '__main__':
    unittest.main()

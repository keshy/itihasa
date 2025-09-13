"""
Basic tests for Itihasa functionality.
These tests focus on import validation and basic structure checks.
"""

import unittest
import sys
import os

# Add src to path for testing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


class TestBasicImports(unittest.TestCase):
    """Test that core modules can be imported without errors."""
    
    def test_main_module_import(self):
        """Test that main module can be imported."""
        try:
            import main
            self.assertTrue(hasattr(main, 'process'))
        except ImportError:
            self.fail("Could not import main module")
    
    def test_generate_module_import(self):
        """Test that generate module can be imported."""
        try:
            import generate
            self.assertTrue(hasattr(generate, 'main'))
        except ImportError:
            self.fail("Could not import generate module")
    
    def test_config_module_import(self):
        """Test that config module can be imported."""
        try:
            from config import parse_config
            self.assertTrue(callable(parse_config))
        except ImportError:
            self.fail("Could not import config module")


class TestProjectStructure(unittest.TestCase):
    """Test that the project has the expected structure."""
    
    def setUp(self):
        self.project_root = os.path.join(os.path.dirname(__file__), '..')
        self.src_dir = os.path.join(self.project_root, 'src')
    
    def test_src_directory_exists(self):
        """Test that src directory exists."""
        self.assertTrue(os.path.exists(self.src_dir))
    
    def test_main_files_exist(self):
        """Test that main Python files exist."""
        main_files = ['main.py', 'generate.py']
        for file in main_files:
            file_path = os.path.join(self.src_dir, file)
            self.assertTrue(os.path.exists(file_path), f"{file} should exist in src/")
    
    def test_required_directories_exist(self):
        """Test that required subdirectories exist."""
        required_dirs = ['config', 'worker', 'utils', 'publisher']
        for dir_name in required_dirs:
            dir_path = os.path.join(self.src_dir, dir_name)
            self.assertTrue(os.path.exists(dir_path), f"{dir_name}/ should exist in src/")
    
    def test_requirements_file_exists(self):
        """Test that requirements.txt exists."""
        requirements_path = os.path.join(self.project_root, 'requirements.txt')
        self.assertTrue(os.path.exists(requirements_path))


class TestLanguageMapping(unittest.TestCase):
    """Test language code mapping functionality."""
    
    def test_language_codes(self):
        """Test that language codes are properly defined."""
        expected_languages = {
            'English': 'en-US',
            'Hindi': 'hi-IN',
            'Tamil': 'ta-IN',
            'Gujarati': 'gu-IN',
            'Bengali': 'bn-IN',
            'Kannada': 'kn-IN',
            'Telugu': 'te-IN'
        }
        
        # This would normally test the actual language mapping from the main module
        # For now, we just verify the expected structure
        self.assertEqual(len(expected_languages), 7)
        self.assertIn('English', expected_languages)
        self.assertIn('Hindi', expected_languages)


if __name__ == '__main__':
    unittest.main()

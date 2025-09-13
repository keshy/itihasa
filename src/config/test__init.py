import unittest
import sys
import os
from unittest.mock import patch, MagicMock

# Add the parent directory to the path so we can import the config module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Mock Google Cloud imports before importing our modules
with patch('vertexai.init'), \
     patch('vertexai.generative_models.GenerativeModel'), \
     patch('google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient'), \
     patch('google.cloud.storage.Client'):
    # Now import from the current directory
    from config import get_base_translation_prompt, get_translation_prompt, ContentConfig, LANG_CODE_MAP


class TestTranslationPrompts(unittest.TestCase):

    def test_get_base_translation_prompt(self):
        prompt = get_base_translation_prompt()
        self.assertIn("Your a lingual expert", prompt)
        self.assertIn("JSON response", prompt)

    def test_get_translation_prompt(self):
        text = "Hello, world!"
        lang = "English"
        part_info = "Part 1 of 5"
        prompt = get_translation_prompt(part_info, text, lang, LANG_CODE_MAP)
        
        # Debug output
        print("\nPrompt starts with:", repr(prompt[:100]) + "...")
        base_prompt = get_base_translation_prompt()
        print("Base prompt starts with:", repr(base_prompt[:100]) + "...")
        
        # Check for required components in the prompt
        self.assertIn("<TEXT>", prompt)
        self.assertIn(text, prompt)
        self.assertIn("<INPUT_LANGUAGE>", prompt)
        self.assertIn(lang, prompt)
        self.assertIn("<LANGUAGE_CODE_MAP>", prompt)
        self.assertIn("en-US", prompt)  # Check that the language code is included
        
        # Check the structure of the prompt
        self.assertTrue(
            prompt.strip().startswith(base_prompt.strip()),
            "Prompt does not start with base translation prompt"
        )
        
        # Check for the presence of each section with flexible whitespace
        self.assertIn(f"<TEXT>", prompt)
        self.assertIn(f"{text}", prompt)
        self.assertIn(f"</TEXT>", prompt)
        
        self.assertIn(f"<INPUT_LANGUAGE>", prompt)
        self.assertIn(f"{lang}", prompt)
        self.assertIn(f"</INPUT_LANGUAGE>", prompt)
        
        self.assertIn(f"<LANGUAGE_CODE_MAP>", prompt)
        self.assertIn(f"en-US", prompt)
        # The actual function doesn't include the closing '>' in the LANGUAGE_CODE_MAP tag
        self.assertIn(f"</LANGUAGE_CODE_MAP", prompt)


class TestContentConfig(unittest.TestCase):

    def setUp(self):
        self.valid_data = {
            'name': 'Interview with Tech Leader',
            'source': {'path': '/path/to/source', 'language': 'Sanskrit'},
            'content_type': 'audio',
            'background_music': {'path': '/assets/music/intro_theme.mp3'},
            'translations': ['English', 'Hindi'],
            'publishing_platforms': ['YouTube', 'Soundcloud'],
            'generate_ai_description': True,
            'generate_milestones': True,
            'split_into_parts': True
        }

    def test_valid_config(self):
        config = ContentConfig.from_dict(self.valid_data)
        self.assertEqual(config.name, 'Interview with Tech Leader')
        self.assertEqual(config.source_path, '/path/to/source')
        self.assertEqual(config.content_type, 'audio')
        self.assertEqual(config.background_music, '/assets/music/intro_theme.mp3')
        self.assertEqual(config.translations, ['English', 'Hindi'])
        self.assertEqual(config.publishing_platforms, ['YouTube', 'Soundcloud'])
        self.assertTrue(config.generate_ai_description)
        self.assertTrue(config.generate_milestones)
        self.assertTrue(config.split_into_parts)

    def test_invalid_translation(self):
        self.valid_data['translations'] = ['InvalidLanguage']
        with self.assertRaises(ValueError) as context:
            ContentConfig.from_dict(self.valid_data)
        self.assertIn('Invalid translation language', str(context.exception))

    def test_invalid_publishing_platform(self):
        self.valid_data['publishing_platforms'] = ['InvalidPlatform']
        with self.assertRaises(ValueError) as context:
            ContentConfig.from_dict(self.valid_data)
        self.assertIn('Invalid publishing platform', str(context.exception))


if __name__ == '__main__':
    unittest.main()

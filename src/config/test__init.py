import unittest
from src.config import get_base_translation_prompt, get_translation_prompt, ContentConfig


class TestTranslationPrompts(unittest.TestCase):

    def test_get_base_translation_prompt(self):
        prompt = get_base_translation_prompt()
        self.assertIn("Your a lingual expert", prompt)
        self.assertIn("JSON response", prompt)

    def test_get_translation_prompt(self):
        text = "Hello, world!"
        lang = "English"
        prompt = get_translation_prompt(text, lang, {"English": "en"})
        self.assertIn("<TEXT>", prompt)
        self.assertIn(text, prompt)
        self.assertIn("<INPUT_LANGUAGE>", prompt)
        self.assertIn(lang, prompt)
        self.assertIn("<LANGUAGE_CODE_MAP>", prompt)


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

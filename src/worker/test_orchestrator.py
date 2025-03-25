import unittest
from unittest.mock import patch, MagicMock
from src.worker.orchestrator import ContentCurator, ContentConfig


class TestContentCurator(unittest.TestCase):

    @patch('src.worker.orchestrator.texttospeech.TextToSpeechLongAudioSynthesizeClient')
    def setUp(self, MockTTSClient):
        self.mock_tts_client = MockTTSClient.return_value
        self.config = ContentConfig(
            name='Test Content',
            source_path='/path/to/source',
            source_lang='English',
            source_type='audio',
            background_music=[],
            translations=['English'],
            publishing_platforms=['YouTube'],
            generate_ai_description=True,
            generate_milestones=True,
            split_into_parts=True,
            from_chunk=0

        )
        self.curator = ContentCurator(self.config)

    def test_initialization(self):
        self.assertEqual(self.curator.config, self.config)
        self.assertIsNotNone(self.curator.gen_model)
        self.assertIsNotNone(self.curator.tts_client)
        self.assertIsNotNone(self.curator.audio_config)
        self.assertIsNotNone(self.curator.job_id)

    def test_chunkify(self):
        text = "This is a test text. " * 100
        chunks = self.curator.chunkify(text, max_words=10, overlap=0.1)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(len(chunk.split()) <= 10 for chunk in chunks))

    @patch('src.worker.orchestrator.GenerativeModel.generate_content')
    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="This is a test text.")
    def test_curate_file(self, mock_gen, mock_open, mock_isfile):
        mock_gen.return_value = MagicMock(text='{"status": "pass", "answer": "Translated text"}')
        self.curator.curate()
        mock_open.assert_called_once_with('/path/to/source')

    @patch('src.worker.orchestrator.GenerativeModel.generate_content')
    @patch('os.path.isfile', return_value=False)
    @patch('os.walk', return_value=[('/path/to/source', [], ['file1.txt'])])
    @patch('builtins.open', new_callable=unittest.mock.mock_open, read_data="This is a test text.")
    def test_curate_directory(self, mock_gen, mock_open, mock_isfile, mock_walk):
        mock_gen.return_value = MagicMock(text='{"status": "pass", "answer": "Translated text"}')
        self.curator.curate()
        mock_open.assert_called_once_with('/path/to/source')

    @patch.object(ContentCurator, '_translate')
    def test_process(self, mock_translate):
        text = "This is a test text. " * 100
        self.curator._process(text)
        self.assertTrue(mock_translate.called)

    @patch('src.worker.orchestrator.GenerativeModel.generate_content')
    def test_translate(self, mock_generate_content):
        mock_generate_content.return_value = MagicMock(text='{"status": "pass", "answer": "Translated text"}')
        self.curator._translate(0, "This is a test text.")
        self.assertTrue(mock_generate_content.called)


if __name__ == '__main__':
    unittest.main()

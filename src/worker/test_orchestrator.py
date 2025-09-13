import unittest
import sys
import os
from unittest.mock import patch, MagicMock, mock_open

# Add the project root to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

# Mock Google Cloud imports before importing our modules
with patch('vertexai.init'), \
     patch('vertexai.generative_models.GenerativeModel'), \
     patch('google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient'), \
     patch('google.cloud.storage.Client'), \
     patch('vertexai.vision_models.ImageGenerationModel'), \
     patch('src.publisher.Publisher'):
    # Now import the modules
    from src.worker.orchestrator import ContentCurator, ContentConfig


class TestContentCurator(unittest.TestCase):

    def setUp(self):
        # Mock the environment variables
        self.patcher = patch.dict('os.environ', {
            'GCP_PARENT_PROJECT': 'test-project',
            'GCP_LOCATION': 'us-central1',
            'VERTEX_MODEL_ID': 'gemini-2.0-flash-001',
            'GCS_BUCKET': 'gs://test-bucket'
        })
        self.patcher.start()
        
        # Create a mock config
        self.config = ContentConfig(
            id='test_id',
            name='Test Content',
            source_path='/path/to/source',
            source_type='audio',
            source_lang='English',
            background_music=[],
            translations=['English'],
            publishing_platforms=['YouTube'],
            generate_ai_description=True,
            generate_milestones=True,
            split_into_parts=True,
            from_chunk=0
        )
        
        # Mock the Google Cloud clients
        with patch('vertexai.generative_models.GenerativeModel') as MockGenModel, \
             patch('google.cloud.texttospeech.TextToSpeechLongAudioSynthesizeClient') as MockTTSClient, \
             patch('google.cloud.storage.Client') as MockStorageClient, \
             patch('vertexai.vision_models.ImageGenerationModel') as MockImageModel, \
             patch('src.publisher.Publisher') as MockPublisher:
            
            # Configure the mocks
            self.mock_gen_model = MockGenModel.return_value
            self.mock_tts_client = MockTTSClient.return_value
            self.mock_storage_client = MockStorageClient.return_value
            self.mock_image_model = MockImageModel.return_value
            self.mock_publisher = MockPublisher.return_value
            
            # Configure storage client
            self.mock_bucket = MagicMock()
            self.mock_storage_client.bucket.return_value = self.mock_bucket
            
            # Mock the from_pretrained method for ImageGenerationModel
            MockImageModel.from_pretrained.return_value = self.mock_image_model
            
            # Create the curator instance
            self.curator = ContentCurator(self.config)
    
    def tearDown(self):
        self.patcher.stop()

    def test_initialization(self):
        self.assertEqual(self.curator.config, self.config)
        self.assertIsNotNone(self.curator.gen_model)
        self.assertIsNotNone(self.curator.tts_client)
        self.assertIsNotNone(self.curator.audio_config)
        self.assertIsNotNone(self.curator.job_id)

    def test_chunkify(self):
        text = "This is a test text. \n" * 100
        chunks = self.curator.chunkify(text, max_lines_per_chunk=10, overlap=0.1)
        self.assertTrue(len(chunks) > 1)
        self.assertTrue(all(chunk in text for chunk in chunks))
        self.assertTrue(all(chunk.count('\n') >= 1 for chunk in chunks))
        self.assertTrue(all(chunk.count('\n') <= 10 for chunk in chunks))

    @patch('os.path.isfile', return_value=True)
    @patch('builtins.open', new_callable=mock_open, read_data="This is a test text.")
    def test_curate_file(self, mock_file, mock_isfile):
        # Mock the _process method to prevent actual processing
        with patch.object(self.curator, '_process') as mock_process:
            self.curator.curate()
            mock_file.assert_called_once_with('/path/to/source', 'r')
            mock_process.assert_called_once()

    @patch('os.path.isfile', return_value=False)
    @patch('os.walk', return_value=[('/path/to/source', [], ['file1.txt'])])
    @patch('builtins.open', new_callable=mock_open, read_data="This is a test text.")
    def test_curate_directory(self, mock_file, mock_walk, mock_isfile):
        # Mock the _process method to prevent actual processing
        with patch.object(self.curator, '_process') as mock_process:
            self.curator.curate()
            mock_file.assert_called_once_with('/path/to/source/file1.txt', 'r')
            mock_process.assert_called_once()

    @patch.object(ContentCurator, '_translate')
    def test_process(self, mock_translate):
        text = "This is a test text. " * 100
        
        # Test with split_into_parts = True
        self.curator._process(text)
        self.assertTrue(mock_translate.called)
        
        # Test with split_into_parts = False
        mock_translate.reset_mock()
        self.curator.config.split_into_parts = False
        self.curator._process(text)
        mock_translate.assert_called_once_with(0, text)


if __name__ == '__main__':
    unittest.main()

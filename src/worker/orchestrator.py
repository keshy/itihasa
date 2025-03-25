import json
import logging
import os
import re
import uuid

import vertexai
from vertexai.generative_models import GenerativeModel
from google.cloud import texttospeech

from src.config import LANG_CODE_MAP, get_translation_prompt, ContentConfig

PROJECT_ID = 'prisma-cortex-playground'
MODEL_ID = "gemini-2.0-flash-001"
REGION = 'us-central1'
vertexai.init(project=PROJECT_ID, location=REGION)
# Update logging format to include job_id
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(job_id)s - %(message)s')


class JobIDFilter(logging.Filter):
    def __init__(self, job_id):
        super().__init__()
        self.job_id = job_id

    def filter(self, record):
        record.job_id = self.job_id
        return True


class ContentCurator:
    def __init__(self, config: ContentConfig):
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.gen_model = GenerativeModel(MODEL_ID)
        self.tts_client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.5
        )
        self.job_id = uuid.uuid4()
        self.retry_from_chunk = self.config.from_chunk
        # Add JobIDFilter to the logger
        job_id_filter = JobIDFilter(self.job_id)
        self.logger.addFilter(job_id_filter)

    def chunkify(self, text, max_words=1000, overlap=0.2):
        words = text.split()
        chunks = []
        chunk = []
        chunk_word_count = 0
        overlap_count = int(max_words * overlap)
        current_chunk = 0

        for word in words:
            chunk.append(word)
            chunk_word_count += 1

            if chunk_word_count >= max_words:
                # Ensure the chunk ends at a line break or a full stop
                while chunk and not re.match(r'[.\n]', chunk[-1]):
                    chunk_word_count -= 1
                    chunk.pop()

                if current_chunk >= self.config.from_chunk:
                    chunks.append(' '.join(chunk))
                chunk = chunk[-overlap_count:]
                chunk_word_count = len(chunk)
                current_chunk += 1

        if chunk and current_chunk >= self.config.from_chunk:
            chunks.append(' '.join(chunk))

        return chunks

    def curate(self):
        # open the source file if its file or if its folder, start iterating over the files
        if os.path.isfile(self.config.source_path):
            with open(self.config.source_path, 'r') as file:
                text = file.read()
                self._process(text)
        else:
            for root, dirs, files in os.walk(self.config.source_path):
                for file in files:
                    with open(os.path.join(root, file), 'r') as f:
                        text = f.read()
                        self._process(text)

    def _process(self, text):
        if self.config.split_into_parts:
            chunks = self.chunkify(text)
            for i, chunk in enumerate(chunks):
                self._translate(i + self.config.from_chunk, chunk)
        else:
            self._translate(0, text)

    def _translate(self, chunk_number, text):
        prompt = get_translation_prompt(text, self.config)
        response = self.gen_model.generate_content(contents=prompt)
        for n in self.config.translations:

            sanitized_response = None
            try:
                tx = response.text.replace('```json', '')
                tx = tx.replace('```', '')
                response_dict = json.loads(tx)
                if response_dict.get('status') != 'pass':
                    error = f'⚡Could not translate...'
                    self.logger.error(error)
                else:
                    sanitized_response = response_dict.get('answer')
            except Exception as e:
                error = f'⚡Could not translate due to a run time exception: {e}'
                self.logger.error(error)
            if sanitized_response:
                self._synthesize(chunk_number, sanitized_response, n)
            else:
                self.logger.warning("Skipping synthesis due to error in translation.")

    def _synthesize(self, part_number, tx, n):
        voice_name = f'{n}-Wavenet-A'
        language_code = LANG_CODE_MAP[n]
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
        file_name = f'{self.config.name}-part-{part_number}-{language_code}' if part_number > 0 else f'{self.config.name}-{language_code}'
        request = texttospeech.SynthesizeLongAudioRequest(
            parent=os.getenv("GCP_PARENT_PROJECT_LOCATION"),
            input={'text': tx},
            audio_config=self.audio_config,
            voice=voice,
            output_gcs_uri=f'{os.getenv("GCS_BUCKET")}/{self.job_id}/{file_name}'
        )
        response = self.tts_client.synthesize_long_audio(request=request)
        self.logger.info(f"Synthesizing part {part_number} in {n} language")
        self.logger.info(f"Synthesis response: {response}")
        self.logger.info(f"Synthesized audio file: {file_name}")


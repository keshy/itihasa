import json
import logging
import os
import uuid
from google.cloud import storage
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
from google.cloud import texttospeech
from publisher import Publisher
import concurrent.futures

from config import LANG_CODE_MAP, get_translation_prompt, ContentConfig

# Update logging format to include job_id
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(job_id)s - %(message)s')
vertexai.init(project=os.getenv("GCP_PARENT_PROJECT"), location=os.getenv("GCP_LOCATION"))


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
        self.gen_model = GenerativeModel(os.getenv("VERTEX_MODEL_ID", "gemini-2.0-flash-001"))
        self.tts_client = texttospeech.TextToSpeechLongAudioSynthesizeClient()
        self.audio_config = texttospeech.AudioConfig(
            audio_encoding=texttospeech.AudioEncoding.LINEAR16,
            speaking_rate=0.85
        )
        self.target_languages = config.translations
        self.job_id = uuid.uuid4()
        self.publisher = Publisher()
        self.retry_from_chunk = self.config.from_chunk
        # Add JobIDFilter to the logger
        job_id_filter = JobIDFilter(self.job_id)
        self.chunks = []
        self.logger.addFilter(job_id_filter)
        self.storage_client = storage.Client()
        self.bucket = self.storage_client.bucket(os.getenv("GCS_BUCKET").split("://")[1])

    def chunkify(self, text, max_lines_per_chunk=100, overlap=0.02):
        # split text into chunks of 100 lines with 20% overlap
        lines = text.splitlines()
        chunks = []
        for i in range(0, len(lines), max_lines_per_chunk):
            chunk = lines[i:i + max_lines_per_chunk]
            if i > 0:
                o = lines[i - int(max_lines_per_chunk * overlap):i]
                chunk = o + chunk
            chunks.append('\n'.join(chunk))
        return chunks

    def curate(self):
        # open the source file if its file or if its folder, start iterating over the files
        if os.path.isfile(self.config.source_path):
            with open(self.config.source_path, 'r') as file:
                text = file.read()
                self._process(text)
        else:
            for root, dirs, files in os.walk(self.config.source_path):
                files.sort()
                for file in files:
                    if file == 'changelog':
                        continue
                    with open(os.path.join(root, file), 'r') as f:
                        text = f.read()
                        self._process(text)
                        print('Completed processing file:', file)

    def _process(self, text):
        if self.config.split_into_parts:
            self.chunks = self.chunkify(text)
            for i, chunk in enumerate(self.chunks):
                self._translate(i + self.config.from_chunk + 1, chunk)

            self.config.from_chunk = len(self.chunks) + self.config.from_chunk
        else:
            self._translate(0, text)
            self.config.from_chunk = 1

    def _translate(self, chunk_number, text):
        # get part_info from the chunk number and total number of chunks
        part_info = f'Part {chunk_number + 1} of {len(self.chunks)}' if self.chunks else ''
        prompt = get_translation_prompt(part_info, text, self.config.source_language,
                                        {k: LANG_CODE_MAP[k] for k in self.target_languages})
        response = self.gen_model.generate_content(contents=prompt,
                                                   generation_config=GenerationConfig(max_output_tokens=4000,
                                                                                      temperature=0.2))

        for n in self.config.translations:
            sanitized_response = None
            answer = ''
            try:
                tx = response.text.replace('```json', '')
                tx = tx.replace('```', '')
                answer = tx
                response_dict = json.loads(tx)
                if not response_dict.get('answer'):
                    error = f'⚡Could not translate...'
                    self.logger.error(error)
                else:
                    sanitized_response = response_dict['answer'][LANG_CODE_MAP.get(n)]
            except Exception as e:
                error = f'⚡Could not load json due to a run time exception for answer {answer}: {e}'
                self.logger.error(error)
            if sanitized_response:
                key_name = self._synthesize(chunk_number, sanitized_response, n)
                self.publisher.process_video(key=key_name)
            else:
                self.logger.warning("Skipping synthesis due to error in translation.")

    def _synthesize(self, part_number, tx, n):
        voice_name = str(f'{LANG_CODE_MAP.get(n)}-Standard-B')
        language_code = LANG_CODE_MAP.get(n)
        voice = texttospeech.VoiceSelectionParams(language_code=language_code, name=voice_name)
        key_name = f'{language_code}/{self.config.id}/{self.config.name}-part-{part_number}' if part_number > 0 \
            else f'{language_code}/{self.config.id}/{self.config.name}'

        request = texttospeech.SynthesizeLongAudioRequest(
            parent=os.getenv("GCP_PARENT_PROJECT_LOCATION"),
            input={'text': tx},
            audio_config=self.audio_config,
            voice=voice,
            output_gcs_uri=f'{os.getenv("GCS_BUCKET")}/{key_name}/audio.wav'
        )
        response = self.tts_client.synthesize_long_audio(request=request)
        # also upload tx as raw translated text to the gcs bucket
        blob = self.bucket.blob(f'{key_name}/subtitles.txt')
        blob.upload_from_string(data=tx, content_type="text/plain; charset=utf-8")
        self.logger.info(f"Synthesizing part {part_number} in {n} language")
        self.logger.info(f"Synthesis response: {response}")
        self.logger.info(f"Synthesized audio file: {key_name}/audio.wav")
        return key_name

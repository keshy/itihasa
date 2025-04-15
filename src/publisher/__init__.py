import os

import vertexai
from google.cloud import storage
from vertexai.generative_models import GenerativeModel, GenerationConfig
import logging
import moviepy.audio.fx.all as afx

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from vertexai.vision_models import ImageGenerationModel

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(job_id)s - %(message)s')
vertexai.init(project=os.getenv("GCP_PARENT_PROJECT"), location=os.getenv("GCP_LOCATION"))


class Publisher:

    def __init__(self, bucket=None, description=None):

        self.bgm = './bgm.mp3'
        self.storage_client = storage.Client()
        self.img_model = GenerativeModel("gemini-pro-vision")
        self.img_options = GenerationConfig(temperature=0.75, max_output_tokens=2048)

        self.bucket = self.storage_client.bucket(os.getenv("GCS_BUCKET").split("://")[1] if bucket is None else bucket)
        self.logger = logging.getLogger(__name__)
        self.tmp_dir = os.getenv("TMP_DIR", "/tmp")
        self.description = description

    def add_bgm(self, key, bgm_path=None, bgm_volume=0.5, clear_tmp=True):
        u_blob = self.bucket.blob(f'{key}/staging_audio.mp3')
        content_path = f'{self.tmp_dir}/{key.rsplit("/")[-1]}-content.wav'
        merged_audio_path = f'{self.tmp_dir}/{key.rsplit("/")[-1]}-merged.mp3'
        gcs_path_for_merged_audio = f'{key}/staging_audio.mp3'
        if u_blob.exists():
            self.logger.info(f"File already exists in GCS: {u_blob.name}")
            u_blob.download_to_filename(merged_audio_path)
            return merged_audio_path
        if bgm_path:
            self.bgm = bgm_path

        d_blob = self.bucket.blob(f'{key}/audio.wav')
        d_blob.download_to_filename(content_path)

        audio1 = AudioFileClip(content_path)
        audio2 = AudioFileClip(self.bgm)
        audio2 = afx.volumex(audio2, bgm_volume)
        audio2 = afx.audio_loop(audio2, duration=audio1.duration)
        final_audio = CompositeAudioClip([audio1, audio2])
        final_audio = final_audio.set_duration(audio1.duration)
        final_audio.write_audiofile(merged_audio_path, codec="libmp3lame", fps=44100)
        audio1.close()
        audio2.close()
        final_audio.close()
        # upload file to gcs
        u_blob = self.bucket.blob(gcs_path_for_merged_audio)
        u_blob.upload_from_filename(merged_audio_path)
        # delete local file
        os.remove(content_path)
        if clear_tmp:
            os.remove(merged_audio_path)
        return gcs_path_for_merged_audio if clear_tmp else merged_audio_path

    def process_video(self, key, bgm_path=None):

        # get subtitles file from gcs at key
        # summarize information in a prompt to llm to generate relevant image for part.
        # add image as a clip to the video and  add audio to the video
        merged_audio = self.add_bgm(key, bgm_path=bgm_path, clear_tmp=False)
        if not merged_audio:
            self.logger.error("Failed to add BGM")
            return
        # load audio file from disk
        ad = AudioFileClip(merged_audio)
        # generate image based on summary of subtitles using llm
        img = self.generate_image(key)
        if not img:
            self.logger.error("Failed to generate image")
            # use default image
            img = './default_image.jpg'

    def generate_image(self, key):
        # generate image based on summary of subtitles using llm
        # use vertexai to generate image
        blob = self.bucket.blob(key + '/subtitles.txt')
        text = blob.download_as_bytes().decode('utf-8')
        img_gen_prompt = f"""
                    Generate an image based on the following text provided in <TEXT> field as a summary of a video. 
                    Include the following guardrails in your response:
                    - Convert <TEXT> into english summary and use this to generate an image. 
                    - The image must be in a 16:9 aspect ratio.
                    - The image must be in a high resolution.
                    - The image must be in a format that is compatible with video editing software.
                    - The image generation leverages the broader context of the video as specified in <DESCRIPTION> field. If its empty - then use your best judgement.
                    - Generate only 1 single image. 
                    - The response must only be a valid JSON response. No other content should be returned.
                    - JSON must only include 1 field - {{"image": "<base64_encoded_image>"}}. The image field must be a base64 encoded image.
                    - Image format must be in png format. 

                    <TEXT>
                    {text}
                    </TEXT>

                    <DESCRIPTION>
                    {self.description}
                    </DESCRIPTION>
                """
        generation_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")

        images = generation_model.generate_images(
            prompt=img_gen_prompt,
            number_of_images=4,
            aspect_ratio="1:1",
            negative_prompt="",
            add_watermark=True,
        )

        return images[0]

    def publish(self):
        pass


if __name__ == '__main__':
    p = Publisher(bucket="ithihasa", description="Old mythology from india")
    p.process_video(key='ta-IN/mahabharat/Mahabharat - As written by Vyasa-part-1', bgm_path='../bgm.mp3')

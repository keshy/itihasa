import io
import json
import os

import vertexai
from google.cloud import storage
from moviepy.video.VideoClip import ImageClip
from vertexai.generative_models import GenerativeModel, GenerationConfig
import logging
import moviepy.audio.fx.all as afx

from moviepy.audio.AudioClip import CompositeAudioClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from vertexai.vision_models import ImageGenerationModel
from PIL import Image as PILImage

from config import get_part_summary_for_img_prompt, get_image_prompt

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(job_id)s - %(message)s')
vertexai.init(project=os.getenv("GCP_PARENT_PROJECT"), location=os.getenv("GCP_LOCATION"))


class Publisher:

    def __init__(self, bucket=None, description=None):

        self.bgm = '../bgm.mp3'
        self.default_cover = '../default_cover.png'
        self.storage_client = storage.Client()
        self.gen_model = GenerativeModel(os.getenv("VERTEX_MODEL_ID", "gemini-2.0-flash-001"))
        self.img_model = ImageGenerationModel.from_pretrained("imagen-3.0-generate-002")
        self.img_options = GenerationConfig(temperature=0.75, max_output_tokens=2048)

        self.bucket = self.storage_client.bucket(os.getenv("GCS_BUCKET").split("://")[1] if bucket is None else bucket)
        self.logger = logging.getLogger(__name__)
        self.tmp_dir = os.getenv("TMP_DIR", "/tmp")
        self.description = description
        self.content_path = f'{self.tmp_dir}/%s-content.wav'
        self.img_path = f'{self.tmp_dir}/%s-image.png'
        self.merged_audio_path = f'{self.tmp_dir}/%s-merged.mp3'
        self.staging_audio_path = '%s/staging_audio.mp3'
        self.tmp_video_path = f'{self.tmp_dir}/%s-video.mp4'
        self.staging_video_path = '%s/staging_video.mp4'

    def add_bgm(self, key, bgm_path=None, bgm_volume=0.25, clear_tmp=True):
        u_blob = self.bucket.blob(self.staging_audio_path % key)
        content_path = self.content_path % key.rsplit("/")[-1]
        merged_audio_path = self.merged_audio_path % key.rsplit("/")[-1]
        gcs_path_for_merged_audio = self.staging_audio_path % key
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
        v_blob = self.bucket.blob(f'{key}/staging_video.mp4')
        if v_blob.exists():
            self.logger.info(f"File already exists in GCS: {v_blob.name}")
            return
        merged_audio = self.add_bgm(key, bgm_path=bgm_path, clear_tmp=False)
        if not merged_audio:
            self.logger.error("Failed to add BGM")
            return
        # load audio file from disk
        ad = AudioFileClip(merged_audio)
        tmp_img_path = self.img_path % key.rsplit("/")[-1]
        u_blob = self.bucket.blob(f'{key}/staging_image.png')
        if u_blob.exists():
            self.logger.info(f"File already exists in GCS: {u_blob.name}")
            u_blob.download_to_filename(tmp_img_path)
        else:
            # generate image based on summary of subtitles using llm
            img, summary = self.generate_image(key)
            if not img:
                self.logger.error("Failed to generate image using AI - defaulting to default image")
                tmp_img_path = self.default_cover
            else:
                if img._mime_type == 'image/png':
                    PILImage.open(io.BytesIO(img._image_bytes)).save(tmp_img_path, format='PNG',
                                                                     quality=95)
                else:
                    self.logger.error("Image is not PNG - defaulting to default image")
                    tmp_img_path = self.default_cover
            u_blob.upload_from_filename(tmp_img_path)
            # upload summary as a file to GCS
            summary_blob = self.bucket.blob(f'{key}/summary.txt')
            summary_blob.upload_from_string(summary)
        # create video clip from image
        clip = ImageClip(img=tmp_img_path, duration=ad.duration)
        # Set the audio of the video clip to the loaded audio clip
        clip = clip.set_audio(ad)
        tmp_file = self.tmp_video_path % key.rsplit("/")[-1]
        clip.write_videofile(tmp_file, codec='mpeg4', fps=1, audio_codec='aac',
                             threads=4)
        ad.close()
        clip.close()
        # upload video to gcs
        v_blob.upload_from_filename(tmp_file)
        # delete local file
        os.remove(tmp_file)
        os.remove(merged_audio)
        os.remove(tmp_img_path)

    def generate_image(self, key):
        # generate image based on summary of subtitles using llm
        # use vertexai to generate image
        blob = self.bucket.blob(key + '/subtitles.txt')
        text = blob.download_as_bytes().decode('utf-8')
        response = self.gen_model.generate_content(get_part_summary_for_img_prompt(text),
                                                   generation_config=GenerationConfig(max_output_tokens=4000,
                                                                                      temperature=0.8))
        try:
            summary_txt = response.text.replace('```json', '')
            summary_txt = summary_txt.replace('```', '')
            summary = json.loads(summary_txt)
            if not summary.get('summary'):
                error = f'⚡Could not generate image...'
                self.logger.error(error)
                return None, None
        except Exception as e:
            error = f'⚡Could not load json due to a run time exception for answer {response}: {e}'
            self.logger.error(error)
            return None, None

        text = summary['summary']
        # generate image using the summary
        images = self.img_model.generate_images(prompt=get_image_prompt(text, self.description),
                                                number_of_images=1,
                                                aspect_ratio="16:9",
                                                negative_prompt="",
                                                add_watermark=True, )
        return images[0], text if len(images.images) > 0 else (None, text)

    def publish(self, key, **kwargs):
        pass


if __name__ == '__main__':
    p = Publisher(bucket="ithihasa", description="Old mythology from india")
    p.process_video(key='ta-IN/mahabharat/Mahabharat - As written by Vyasa-part-1', bgm_path='../bgm.mp3')

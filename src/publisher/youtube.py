import json

from vertexai.generative_models import GenerationConfig

from publisher import Publisher
import os
from config import get_part_summary_in_local_language


class YouTubePublisher(Publisher):

    def __init__(self, bucket=None, description=None, local_lang=None):
        super().__init__(bucket, description)
        self.local_lang = local_lang

    def publish(self, key, **kwargs):
        # Check if the video file exists in GCS
        video_blob = self.bucket.blob(f'{key}/staging_video.mp4')
        subtitles_blob = self.bucket.blob(f'{key}/subtitles.txt')
        summary_blob = self.bucket.blob(f'{key}/summary.txt')
        if not video_blob.exists():
            raise FileNotFoundError(f"Video file not found in GCS: {video_blob.name}")

        summary = None
        # title is last part of the key
        title = key.split("/")[-1]
        # get description from subtitles file calling llm if it exists otherwise use default_summary
        # use summary from summary blob if it exists otherwise use subtitles file
        if summary_blob.exists():
            summary_blob.download_to_filename(f'{self.tmp_dir}/{key.split("/")[-1]}-summary.txt')
            with open(f'{self.tmp_dir}/{key.split("/")[-1]}-summary.txt', 'r') as f:
                summary = f.read()
                summary = self.get_summary(summary)
            # remove summary file
            os.remove(f'{self.tmp_dir}/{key.split("/")[-1]}-summary.txt')
        elif subtitles_blob.exists():
            subtitles_blob.download_to_filename(f'{self.tmp_dir}/{key.split("/")[-1]}-subtitles.txt')
            with open(f'{self.tmp_dir}/{key.split("/")[-1]}-subtitles.txt', 'r') as f:
                subtitles = f.read()
            # Generate a summary using LLM
            summary = self.get_summary(subtitles)
            # remove subtitles file
            os.remove(f'{self.tmp_dir}/{key.split("/")[-1]}-subtitles.txt')
        else:
            summary = self.description

        # tags to be extracted from kwargs
        tags = kwargs.get('tags', [])
        # add tags to description
        description = f"{summary}\n\nTags: {', '.join(tags)}"

        # Download the video file to a temporary location
        local_video_path = f'{self.tmp_dir}/{key.split("/")[-1]}-video.mp4'
        video_blob.download_to_filename(local_video_path)

        # print the file path, the description to use etc.
        print(f"Video file downloaded to: {local_video_path}")
        print(f"Title: {title}")
        print(f"Description: {description}")
        print(f"Tags: {', '.join(tags)}")
        print('****************************************************************')
        # add all of the above details into a map in a tmp file and save it next to the video
        # file

        with open(f'{self.tmp_dir}/{key.split("/")[-1]}-details.json', 'w') as f:
            json.dump({
                'title': title,
                'description': description,
                'tags': tags,
                'video_file': local_video_path
            }, f, indent=4)

        # # Clean up the temporary file
        # os.remove(local_video_path)
        # # remove {key.split("/")[-1]} from tmp_dir
        # os.rmdir(f'{self.tmp_dir}/{key.split("/")[-1]}')

    def get_summary(self, text):
        response = self.gen_model.generate_content(
            get_part_summary_in_local_language(text, self.local_lang),
            generation_config=GenerationConfig(max_output_tokens=4000,
                                               temperature=0.8))
        try:
            summary_txt = response.text.replace('```json', '')
            summary_txt = summary_txt.replace('```', '')
            summary = json.loads(summary_txt)
            if not summary.get('summary'):
                error = f'⚡Could not generate image...'
                self.logger.error(error)
                return None
        except Exception as e:
            error = f'⚡Could not load json due to a run time exception for answer {response}: {e}'
            self.logger.error(error)
            return None
        return summary['summary']

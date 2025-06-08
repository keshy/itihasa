# generate an argparse based script that takes in path to yaml file that contains
# content for a podcast_file as a path, a path to the background score and a path to an image file and compose a final mp4 out of this that's publishable
# the yaml also includes description field that can be used.

import os

import yaml
import argparse
import moviepy.audio.fx.all as afx
from moviepy.audio.AudioClip import CompositeAudioClip


class ContentManifest:
    def __init__(self, name, podcast_paths, bgm, cover_art, description):
        self.name = name
        self.podcast_paths = self._validate_paths(podcast_paths)[0]
        self.bgm = self._validate_paths([bgm])[0]
        self.cover_art = self._validate_paths([cover_art])[0]
        self.description = description

    @staticmethod
    def _validate_paths(paths):
        valid_paths = []
        for path in paths:
            if os.path.exists(os.path.join(os.getcwd(), 'content', path)):
                valid_paths.append(path)
            else:
                raise FileNotFoundError(f"Path does not exist: {path}")
        return valid_paths


def parse_yaml_to_object(yaml_path):
    with open(yaml_path, 'r') as file:
        data = yaml.safe_load(file)

        return ContentManifest(
            name=data.get('name'),
            podcast_paths=data.get('podcast_paths', []),
            bgm=data.get('bgm', []),
            cover_art=data.get('cover_art', []),
            description=data.get('description', "")
        )


# add a method to now combine the bgm, the podcast_path and cover art into an mp4 file. If the bgm is smaller than the podcast - loop it.
def combine_to_mp4(content_manifest, output_path="content"):
    from moviepy.editor import AudioFileClip, ImageClip, concatenate_videoclips
    if not content_manifest.podcast_paths:
        raise ValueError("No podcast paths provided.")
    if not content_manifest.bgm:
        raise ValueError("No background music provided.")
    if not content_manifest.cover_art:
        raise ValueError("No cover art provided.")
    # Load cover art
    cover_art_path = content_manifest.cover_art
    cover_art_clip = ImageClip(cover_art_path).set_duration(0)  # Set duration to 0 for static image
    cover_art_clip = cover_art_clip.set_duration(cover_art_clip.duration)
    # Load podcast audio
    if os.path.exists(content_manifest.podcast_paths):
        audio_clip = AudioFileClip(content_manifest.podcast_paths)
    else:
        raise FileNotFoundError(f"Podcast path does not exist: {content_manifest.podcast_paths}")

    # Load background music
    if os.path.exists(content_manifest.bgm):
        bgm_clip = AudioFileClip(content_manifest.bgm)
    else:
        raise FileNotFoundError(f"BGM path does not exist: {content_manifest.bgm}")

    bgm_clip_updated = afx.volumex(bgm_clip, 0.25)
    bgm_clip_updated = afx.audio_loop(bgm_clip_updated, duration=audio_clip.duration)
    merged_audio = CompositeAudioClip([audio_clip, bgm_clip_updated])
    merged_audio = merged_audio.set_duration(audio_clip.duration)
    final_clip = cover_art_clip.set_audio(merged_audio)
    final_clip = final_clip.set_duration(audio_clip.duration)
    final_clip.write_videofile(filename=content_manifest.name + '.mp4', fps=1, codec='mpeg4',
                               audio_codec='aac', threads=4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse YAML to Python object and validate paths.")
    parser.add_argument("--yaml_path", type=str, help="Path to the YAML file.")
    parser.add_argument("--output_path", type=str, default="./content", help="Path to store the final video.")
    args = parser.parse_args()

    try:
        content_manifest = parse_yaml_to_object(args.yaml_path)
        from pprint import pprint

        pprint(content_manifest.__dict__)
        # Print the content manifest object
        print("\nContent Manifest Object Attributes:")
        for key, value in content_manifest.__dict__.items():
            print(f"{key}: {value}")
        # Ensure output path exists
        if not os.path.exists(args.output_path):
            os.makedirs(args.output_path)
        # Change directory to output path
        os.chdir(args.output_path)
        # Combine to MP4
        combine_to_mp4(content_manifest)
        # Print parsed content manifest
        print("Content Manifest Parsed Successfully:")
    except Exception as e:
        print(f"Error: {e}")

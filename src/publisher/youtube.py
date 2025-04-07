import os

from moviepy.editor import AudioFileClip, CompositeAudioClip
import moviepy.video.fx.all as vfx
import moviepy.audio.fx.all as afx
# merge 2 audio files into one but with one of them on lower volume
from moviepy.video.compositing.concatenate import concatenate
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def merge_audio_files(file1, file2, volume=0.5):
    audio1 = AudioFileClip(file1)
    audio2 = AudioFileClip(file2)
    audio2 = audio2.volumex(volume)
    audio2 = afx.audio_loop(audio2, duration=audio1.duration)
    final_audio = CompositeAudioClip([audio1, audio2])
    final_audio = final_audio.set_duration(audio1.duration)
    final_audio.write_audiofile('1_merged.wav', fps=44100)
    audio1.close()
    audio2.close()
    final_audio.close()
    # create video with the merged audio and a bunch of images slowly fading in and rotating
    # write code
    image_folder = './image'
    image_files = sorted([os.path.join(image_folder, f)
                          for f in os.listdir(image_folder)
                          if f.endswith(('.jpg', '.jpeg', '.png', '.gif'))])

    if not image_files:
        print(f"No valid image files found in: {image_folder}")
        return
    fps = 44100
    clip = ImageSequenceClip(image_files, fps=fps)
    # Set the audio of the video clip to the loaded audio clip
    clip = clip.set_audio(final_audio)
    clip.write_videofile("youtube_ready_video", codec='mpeg4')
    final_audio.close()
    clip.close()

    return "youtube_ready_video"


if __name__ == '__main__':
    file1 = './bgm.mp3'
    file2 = './audio.wav'
    merged_file = merge_audio_files(file2, file1, volume=0.75)
    print(f'Merged file: {merged_file}')

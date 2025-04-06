import os

from moviepy.editor import AudioFileClip, CompositeAudioClip

# merge 2 audio files into one but with one of them on lower volume
from moviepy.video.compositing.concatenate import concatenate
from moviepy.video.io.ImageSequenceClip import ImageSequenceClip


def merge_audio_files(file1, file2, volume=0.5):
    audio1 = AudioFileClip(file1)
    audio2 = AudioFileClip(file2)
    audio2 = audio2.volumex(volume)
    final_audio = CompositeAudioClip([audio1, audio2])
    final_audio = final_audio.set_duration(audio1.duration)
    final_audio.write_audiofile('merged.wav', fps=44100)
    audio1.close()
    audio2.close()
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

    # Ensure the video duration matches the audio duration
    if clip.duration < final_audio.duration:
        # Option 1: Loop the video to match audio duration (simplest but might look repetitive)
        # clip = clip.fx(vfx.loop, duration=audio_clip.duration)

        # Option 2: Extend the last frame to match audio duration (video will freeze at the end)
        last_frame = clip.get_frame(clip.duration - 1 / fps if clip.duration > 0 else 0)
        from moviepy.editor import ImageClip
        extended_frame_clip = ImageClip(last_frame, duration=final_audio.duration - clip.duration)
        clip = concatenate([clip, extended_frame_clip])
        clip = clip.set_audio(final_audio)  # Re-set audio after concatenation

    elif clip.duration > final_audio.duration:
        # Trim the video to match the audio duration
        clip = clip.subclip(0, final_audio.duration)

    clip.write_videofile("youtube_ready_video", codec='libx264', audio_codec='aac')

    final_audio.close()
    clip.close()

    return "youtube_ready_video"


if __name__ == '__main__':
    file1 = './bgm.mp3'
    file2 = './audio.wav'
    merged_file = merge_audio_files(file2, file1, volume=0.75)
    print(f'Merged file: {merged_file}')

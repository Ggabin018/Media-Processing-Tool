import os
from moviepy.video.io.VideoFileClip import VideoFileClip

from src.utils.thread_processing import exec_command


def convert_vid2audio(video_path: str, start_time: int = 0, end_time: int = 0) -> str:
    """ 
    video to mp3
    start_time and end_time in seconds
    """
    video_clip = VideoFileClip(video_path)
    if start_time < 0 or end_time < 0:
        raise Exception("start_time or end_time are negative")
    if end_time == 0:
        end_time = video_clip.duration

    audio_clip = video_clip.audio.subclip(start_time, end_time)

    mp3_path = os.path.splitext(video_path)[0] + ".mp3"
    audio_clip.write_audiofile(mp3_path)

    audio_clip.close()
    video_clip.close()

    return mp3_path


def convert_vid2vid(video_path: str, ext: str) -> str:
    output_video = os.path.splitext(video_path)[0] + "." + ext
    ffmpeg_command = (
        f'ffmpeg -y -i "{video_path}" -c copy "{output_video}"'
    )
    exec_command(ffmpeg_command)
    return output_video

import random

from back_end.audio_manip import audio_combine, audio_replace
from back_end.video_manip import video_compress
from back_end.media_converter import convert_media

from toolbox.progress import task_name
from toolbox.threads import map_in_threads


def pick_audios(videos: list[str], audios: list[str], randomize: bool) -> list[str]:
    """One audio per video: random, or in order (looping over the audios)."""
    if not audios:
        raise ValueError("No audio files")
    if randomize:
        return [random.choice(audios) for _ in videos]
    return [audios[i % len(audios)] for i in range(len(videos))]


def files_compress_videos(files: list[str], bitrate, min_res, vcodec) -> str:
    """Compress every video next to the original (__compressed.mp4)."""
    return '\n'.join(map_in_threads(
        lambda f: video_compress(f, target_bitrate=bitrate, min_resolution=int(min_res), vcodec=vcodec), files))


def files_convert(files: list[str], ext: str) -> str:
    """Convert media files (video or audio) to another format."""
    return '\n'.join(map_in_threads(lambda f: convert_media(f, ext), files))


def files_audio_combine(videos: list[str], audios: list[str], randomize: bool) -> str:
    """Mix an audio file into each video."""
    pairs = list(zip(videos, pick_audios(videos, audios, randomize)))
    return '\n'.join(map_in_threads(lambda p: audio_combine(*p), pairs, name=lambda p: task_name(p[0])))


def files_audio_replace(videos: list[str], audios: list[str], randomize: bool) -> str:
    """Replace the audio of each video."""
    pairs = list(zip(videos, pick_audios(videos, audios, randomize)))
    return '\n'.join(map_in_threads(lambda p: audio_replace(*p), pairs, name=lambda p: task_name(p[0])))


def files_convert_video_to_video(videos: list[str], ext: str) -> str:
    return '\n'.join(map_in_threads(lambda f: convert_media(f, ext), videos))


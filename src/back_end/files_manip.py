import random
from concurrent.futures import ThreadPoolExecutor

from back_end.audio_manip import audio_combine, audio_replace
from back_end.video_manip import video_compress
from back_end.media_converter import convert_media

from toolbox.Parameters import Params

params = Params()

def files_compress_videos(files: list[str], bitrate, min_res, vcodec) -> str:
    """
    compress all videos in a subdir output
    """
    res = []

    def process_file(file):
        res.append(video_compress(file, target_bitrate=bitrate, min_resolution=min_res, vcodec=vcodec))

    with ThreadPoolExecutor(max_workers=params.get_max_workers()) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


def files_convert(files: list[str], ext: str) -> str:
    """
    Convert media files (video or audio) to another format
    """
    res = []

    def process_file(file):
        res.append(convert_media(file, ext))

    with ThreadPoolExecutor(max_workers=params.get_max_workers()) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


def files_audio_combine(videos: list[str], audios: list[str]) -> str:
    """
    combine les vidéos et leurs audios avec les audios d'un autre dossier
    """
    res = []

    def process_file(file):
        audio_to_combine = random.choice(audios)
        res.append(audio_combine(file, audio_to_combine))

    with ThreadPoolExecutor(max_workers=params.get_max_workers()) as executor:
        executor.map(process_file, videos)

    return '\n'.join(res)


def files_audio_replace(videos: list[str], audios: list[str]) -> str:
    """
    replace audios of files with compression
    """
    res = []

    def process_file(file):
        audio_to_combine = random.choice(audios)
        res.append(audio_replace(file, audio_to_combine))

    with ThreadPoolExecutor(max_workers=params.get_max_workers()) as executor:
        executor.map(process_file, videos)

    return '\n'.join(res)


def files_convert_video_to_video(videos: list[str], ext: str) -> str:
    res = []

    def process_file(file):
        res.append(convert_media(file, ext))

    with ThreadPoolExecutor(max_workers=params.get_max_workers()) as executor:
        executor.map(process_file, videos)

    return '\n'.join(res)

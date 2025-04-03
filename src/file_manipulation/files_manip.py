import os
import random
from concurrent.futures import ThreadPoolExecutor

from file_manipulation.audio_modif import audio_combine, audio_replace
from file_manipulation.video_modif import video_compress
from file_manipulation.convert import convert_vid2audio, convert_vid2vid


def files_compress_videos(files: list[str], bitrate: int = 8000) -> str:
    """
    compress all videos in a subdir output
    """
    res = []

    def process_file(file):
        res.append(video_compress(file, target_bitrate=bitrate))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


def files_audio_extract(files: list[str]) -> str:
    """
    extrait les audios des vidéos
    """
    res = []

    def process_file(file):
        res.append(convert_vid2audio(file))

    with ThreadPoolExecutor(max_workers=5) as executor:
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

    with ThreadPoolExecutor(max_workers=5) as executor:
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

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, videos)

    return '\n'.join(res)


def files_convert_video_to_video(videos: list[str], ext: str) -> str:
    res = []

    def process_file(file):
        res.append(convert_vid2vid(file, ext))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, videos)

    return '\n'.join(res)

import os
import random

from back_end.audio_manip import audio_combine, audio_replace, is_audio
from back_end.video_manip import video_compress, is_video
from back_end.media_converter import convert_media
from back_end.files_manip import pick_audios
from toolbox.progress import task_name
from toolbox.threads import map_in_threads


def _list(dir_path: str, keep) -> list[str]:
    """Files of a directory (not recursive) kept by `keep(name)`, sorted, as full paths."""
    return [os.path.join(dir_path, f) for f in sorted(os.listdir(dir_path))
            if keep(f) and os.path.isfile(os.path.join(dir_path, f))]


def dir_compress_videos(dir_path: str, bitrate: int = 8000, min_res: int = 1080, vcodec: str = "hevc_nvenc") -> str:
    """
    compress all videos of a directory into its "output" subdirectory
    :param dir_path: chemin absolue du dossier
    :param bitrate: bitrate in kbps (default: 8000)
    :param min_res: minimum resolution
    :param vcodec: video codec
    """
    output_folder = os.path.join(dir_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    videos = _list(dir_path, is_video)

    def process_file(file):
        output_file = os.path.join(output_folder, os.path.basename(file))
        return video_compress(file, output_file, bitrate, min_res, vcodec)

    return '\n'.join(map_in_threads(process_file, videos))


def compress_videos_dossier_parent(parent_dir: str, bitrate: int, min_res: int, vcodec: str) -> str:
    """
    dir_compress_videos on every direct subdirectory
    :param parent_dir: chemin abs dossier parent
    :param bitrate: bitrate in kbps (default: 8000)
    :param min_res: minimum resolution
    :param vcodec: video codec
    """
    res = []
    for child_dir in sorted(os.listdir(parent_dir)):
        child_dir_path = os.path.join(parent_dir, child_dir)
        if os.path.isdir(child_dir_path) and child_dir != "output":
            res.append(dir_compress_videos(child_dir_path, bitrate, min_res, vcodec))
    return '\n'.join(r for r in res if r)


def dir_convert_media(videos_dir: str, ext: str) -> str:
    """
    convert every mp4 of a directory (e.g. extract audio)
    :param videos_dir: dossier contenant les vidéos
    :param ext: file extension
    """
    files = _list(videos_dir, lambda f: f.lower().endswith(".mp4"))
    return '\n'.join(map_in_threads(lambda f: convert_media(f, ext), files))


def dir_audio_combine(videos_dir: str, audio_dir: str, randomize: bool) -> str:
    """
    mix an audio of audio_dir into every video of videos_dir
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    videos = _list(videos_dir, is_video)
    pairs = list(zip(videos, pick_audios(videos, _list(audio_dir, is_audio), randomize)))
    return '\n'.join(map_in_threads(lambda p: audio_combine(*p), pairs, name=lambda p: task_name(p[0])))


def dir_audio_replace(videos_dir: str, audio_dir: str, randomize: bool) -> str:
    """
    replace the audio of every video of videos_dir by an audio of audio_dir
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    videos = _list(videos_dir, is_video)
    pairs = list(zip(videos, pick_audios(videos, _list(audio_dir, is_audio), randomize)))
    return '\n'.join(map_in_threads(lambda p: audio_replace(*p), pairs, name=lambda p: task_name(p[0])))


def dir_audio_replace_no_thread(videos_dir, audio_dir) -> str:
    """
    combine les vidéos et leurs audios avec les audios d'un autre dossier
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    audio_list = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.lower().endswith(".mp3")]
    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    res = []
    for file in files:
        path_mp4 = os.path.join(videos_dir, file)
        audio_to_combine = random.choice(audio_list)
        res.append(audio_replace(path_mp4, audio_to_combine))

    return '\n'.join(res)


def rename_files(input_dir: str):
    """
    enlève les "__" des noms de fichiers, tolérant aux doublons
    :param input_dir: dossier contenant les fichiers
    """
    files = [file for file in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, file))]

    for file in files:
        index = file.find("__")

        if index != -1:
            new_name = file[:index]

            counter = 1
            while os.path.exists(os.path.join(input_dir, new_name)):
                new_name = f"{file[:index]}_{counter}"
                counter += 1

            old_path = os.path.join(input_dir, file)
            new_path = os.path.join(input_dir, new_name + ".mp4")
            os.rename(old_path, new_path)


def dir_convert_video_to_video(videos_dir: str, ext: str) -> str:
    files = _list(videos_dir, lambda f: f.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm')))
    return '\n'.join(map_in_threads(lambda f: convert_media(f, ext), files))

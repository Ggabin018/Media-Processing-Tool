import os
import random
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

from src.file_manipulation.audio_modif import audio_combine, audio_replace
from src.file_manipulation.video_modif import video_compress
from src.file_manipulation.convert import convert_vid2audio, convert_vid2vid


def dir_compress_videos(dir_path: str, bitrate: int = 8000) -> str:
    """
    Compress all videos in a subdir into an 'output' folder.

    :param dir_path: Absolute path of the folder
    :param bitrate: Target bitrate for compression
    :return: List of output files or messages
    """
    output_folder = os.path.join(dir_path, "output")
    os.makedirs(output_folder, exist_ok=True)

    video_files = [
        os.path.join(dir_path, fichier)
        for fichier in os.listdir(dir_path)
        if fichier.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm'))
    ]

    with ProcessPoolExecutor(max_workers=5) as executor:
        futures = [
            executor.submit(video_compress, file, os.path.join(output_folder, os.path.basename(file)), bitrate)
            for file in video_files
        ]
        results = [future.result() for future in futures]

    return '\n'.join(filter(None, results))  # Remove empty results


def compress_videos_dossier_parent(parent_dir: str):
    """
    use convertir_videos_dossier sur ses sous-dossiers
    :param parent_dir: chemin abs dossier parent
    """
    try:
        # Just subdir, no recursive
        for child_dir in os.listdir(parent_dir):
            child_dir_path = os.path.join(parent_dir, child_dir)

            if os.path.isdir(child_dir_path):
                dir_compress_videos(child_dir_path)
    except Exception as e:
        print(f"Error : {str(e)}")


def dir_audio_extract(videos_dir: str) -> str:
    """
    extrait les audios des vidéos
    :param videos_dir: dossier contenant les vidéos
    """
    res = []

    def process_file(file):
        path_mp4 = os.path.join(videos_dir, file)
        res.append(convert_vid2audio(path_mp4))

    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


def dir_audio_combine(videos_dir: str, audio_dir: str) -> str:
    """
    combine les vidéos et leurs audios avec les audios d'un autre dossier
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    res = []
    audio_list = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.lower().endswith(".mp3")]

    def process_file(file):
        path_mp4 = os.path.join(videos_dir, file)
        audio_to_combine = random.choice(audio_list)
        res.append(audio_combine(path_mp4, audio_to_combine))

    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


def dir_audio_replace(videos_dir: str, audio_dir: str) -> str:
    """
    combine les vidéos et leurs audios avec les audios d'un autre dossier
    replace audio with compression
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    res = []
    audio_list = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.lower().endswith(".mp3")]

    def process_file(file):
        path_mp4 = os.path.join(videos_dir, file)
        audio_to_combine = random.choice(audio_list)
        res.append(audio_replace(path_mp4, audio_to_combine))

    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)


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
    res = []
    files = [os.path.join(videos_dir, file) for file in os.listdir(videos_dir) if
             file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm'))]

    def process_file(file):
        res.append(convert_vid2vid(file, ext))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)

if __name__ == "__main__":
    dir_path = "/home/gabin/Media-Processing-Tool/tests/videos"
    dir_compress_videos(dir_path)
import os
import random
from concurrent.futures import ThreadPoolExecutor

from file_manipulation.audio_modif import audio_combine, audio_replace
from file_manipulation.convertisseur import convertir_en_1080p, convertir_video_to_mp3, conv_video_to_video


def convertir_videos_dossier(dossier_path):
    """
    convertie toutes les vidéos d'un dossier dans un sous-dossier
    :param dossier_path: chemin absolue du dossier
    """
    output_folder = os.path.join(dossier_path, "output")
    os.makedirs(output_folder, exist_ok=True)
    # Liste des fichiers dans le dossier
    video_files = []
    for fichier in os.listdir(dossier_path):
        if fichier.lower().endswith(('.mp4', '.avi', '.mkv', '.mov')):
            video_files.append(os.path.join(dossier_path, fichier))
        elif fichier.lower().endswith('.webm'):
            video_files.append(conv_video_to_video(os.path.join(dossier_path, fichier), "mp4"))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(lambda x: convertir_en_1080p(x, output_folder), video_files)


def convertir_videos_dossier_parent(dossier_parent):
    """
    applique convertir_videos_dossier sur ses sous-dossiers
    :param dossier_parent: chemin abs dossier parent
    """
    try:
        # Parcourt tous les sous-dossiers du dossier parent
        for dossier_fils in os.listdir(dossier_parent):
            dossier_fils_path = os.path.join(dossier_parent, dossier_fils)

            if os.path.isdir(dossier_fils_path):
                convertir_videos_dossier(dossier_fils_path)
    except Exception as e:
        print(f"Erreur lors de la conversion des vidéos dans le dossier parent. Erreur : {str(e)}")

def dir_audio_extract(videos_dir)->str:
    """
    extrait les audios des vidéos
    :param videos_dir: dossier contenant les vidéos
    """
    res = []
    def process_file(file):
        path_mp4 = os.path.join(videos_dir, file)
        res.append(convertir_video_to_mp3(path_mp4))

    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)

def dir_audio_combine(videos_dir, audio_dir):
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

def dir_audio_replace(videos_dir, audio_dir):
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

def dir_audio_replace_no_thread(videos_dir, audio_dir):
    """
    combine les vidéos et leurs audios avec les audios d'un autre dossier
    :param videos_dir: dossier contenant les vidéos
    :param audio_dir: dossier contenant les audios à superposer
    """
    audio_list = [os.path.join(audio_dir, file) for file in os.listdir(audio_dir) if file.lower().endswith(".mp3")]
    files = [file for file in os.listdir(videos_dir) if file.lower().endswith(".mp4")]

    for file in files:
        path_mp4 = os.path.join(videos_dir, file)
        audio_to_combine = random.choice(audio_list)
        audio_replace(path_mp4, audio_to_combine)

def rename_files(input_dir):
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

def dir_convert_video_to_video(videos_dir, ext):
    res = []
    files = [os.path.join(videos_dir, file) for file in os.listdir(videos_dir) if file.lower().endswith(('.mp4', '.avi', '.mkv', '.mov', '.webm'))]
    
    def process_file(file):
            res.append(conv_video_to_video(file, ext))

    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(process_file, files)

    return '\n'.join(res)
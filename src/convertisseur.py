import os
from moviepy.video.io.VideoFileClip import VideoFileClip
from video_modif import get_resolution

from thread import exec


def convertir_en_1080p(video_path, output_folder, target_bitrate=8000):
    """
    convertie une vidéo en 1080p
    :param video_path: path abs de la vidéo
    :param output_folder: dossier de sortie
    :param target_bitrate: bitrate cible
    """
    try:
        width, height = get_resolution(video_path)

        if width >= 1080 or height >= 1080:

            # Nom de la vidéo de sortie
            output_filename = os.path.join(output_folder, os.path.basename(video_path))

            # Calculer le nouveau bitrate en fonction de la résolution cible
            if width > height:
                target_bitrate = int(target_bitrate * 1920 / width)
            else:
                target_bitrate = int(target_bitrate * 1920 / width)

            # Commande FFmpeg pour convertir en 1080p avec CUDA tout en conservant le ratio d'aspect
            if width > height:
                ffmpeg_command = (
                    f'ffmpeg -hwaccel cuda -i "{video_path}" -c:v hevc_nvenc -b:v {target_bitrate}k -vf "scale=-2:1080" -c:a copy -pix_fmt yuv420p "{output_filename}"'
                )
            else:
                ffmpeg_command = (
                    f'ffmpeg -hwaccel cuda -i "{video_path}" -c:v hevc_nvenc -b:v {target_bitrate}k -vf "scale=1080:-2" -c:a copy -pix_fmt yuv420p "{output_filename}"'
                )

            os.system(ffmpeg_command)
        else:
            print(f"La résolution de la vidéo {video_path} est déjà inférieure ou égale à 1080p.")
    except Exception as e:
        print(f"Conversion échouée pour la vidéo {video_path}. Erreur : {str(e)}")


def convertir_video_to_mp3(video_path, start_time=0, end_time=None)->str:
    """ mp4 vers mp3"""
    # Charger la vidéo
    video_clip = VideoFileClip(video_path)

    if not end_time:
        end_time = video_clip.duration  # fin à la fin de la vidéo

    # Extraire la piste audio de la plage spécifiée
    audio_clip = video_clip.audio.subclip(start_time, end_time)

    # Écrire la piste audio dans un fichier MP3
    mp3_path = os.path.splitext(video_path)[0] + ".mp3"
    audio_clip.write_audiofile(mp3_path)

    # Fermer les clips
    audio_clip.close()
    video_clip.close()

    return mp3_path

def conv_video_to_video(video_path, ext)->str:
    output_video = os.path.splitext(video_path)[0] + "." + ext
    ffmpeg_command = (
        f'ffmpeg -y -i "{video_path}" -c copy "{output_video}"'
    )
    exec(ffmpeg_command)
    return output_video
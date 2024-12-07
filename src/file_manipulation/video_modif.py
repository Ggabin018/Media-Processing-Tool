import os
from thread import exec

def get_video_duration(video_path:str)->float:
    """
    :param video_path: chemin absolu de la vidéo
    :return: durée de la vidéo en secondes
    """
    # Commande FFmpeg pour obtenir la durée de la vidéo
    ffmpeg_command = f'ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=p=0 "{video_path}"'

    # Exécution de la commande FFmpeg
    duration_info = os.popen(ffmpeg_command).read().strip()

    # Conversion de la durée en float
    duration = float(duration_info)

    return duration

def get_resolution(video_path:str)->tuple[int,int]:
    """
    :param video_path: chemin abs vidéo
    :return: largeur, hauteur de la vidéo
    """
    # Commande FFmpeg pour obtenir les informations sur la vidéo
    ffmpeg_command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{video_path}"'

    # Exécution de la commande FFmpeg
    resolution_info = os.popen(ffmpeg_command).read()

    # Extraction de la largeur et de la hauteur de la résolution
    width, height = map(int, resolution_info.split('x'))

    return width, height


def video_cut(input_video:str, start=None, end=None)->str:
    """
    créer un extrait d'une vidéo
    :param input_video: path de la video
    :param start: format "HH:MM:SS"
    :param end: format "HH:MM:SS"
    """
    start_option = f"-ss {start}" if start is not None and start != "" else ""
    end_option = f"-to {end}" if end is not None and end != "" else ""

    output_video = os.path.splitext(input_video)[0] + "__cut.mp4"
    ffmpeg_command = (
        #f'ffmpeg -y -i "{input_video}" {start_option} {end_option} -c copy "{output_video}"' # fast
        f'ffmpeg -y -i "{input_video}" {start_option} {end_option} "{output_video}"'          # slow but no bug
    )

    exec(ffmpeg_command)
    
    return output_video


def video_upgrade_quality(input_video:str, mul:int)->str:
    """
    multiplie la résolution de la vidéo d'entrer
    WARNING BUG peut crash sur certaines videos
    :param input_video:
    :param mul:
    """
    output_video = os.path.splitext(input_video)[0] + f"__up{mul}.mp4"
    ffmpeg_command = (
        f'ffmpeg -i "{input_video}" -vf "scale=iw*{mul}:ih*{mul},unsharp=5:5:1.0:5:5:0.0, hqdn3d=luma_spatial=4:chroma_spatial=4:luma_tmp=4:chroma_tmp=4" -c:a copy "{output_video}"'
    )
    exec(ffmpeg_command)
    return output_video

import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip
from video_modif import get_video_duration


def apply_reverb(input_path):
    reverb_parameters = "0.8:0.9:1000:0.6"
    output_path = os.path.splitext(input_path)[0] + "__reverb.mp3"

    # Construire la commande FFmpeg
    ffmpeg_command = (
        f'ffmpeg -y -i "{input_path}" -af "aecho={reverb_parameters}" -c:a libmp3lame -q:a 2 "{output_path}"'
    )
    os.system(ffmpeg_command)


def apply_deep_voice(input_path, sampling_rate=0.8):
    output_path = os.path.splitext(input_path)[0] + f"__deep{sampling_rate}.mp3"

    ffmpeg_command = (
        f'ffmpeg -y -i "{input_path}" -af "asetrate={sampling_rate}*44100" -c:a libmp3lame -q:a 2 "{output_path}"'
    )

    os.system(ffmpeg_command)


def multiply_and_write_audio(input_audio_path, output_audio_path, multiplier):
    """
    multiplie une piste audio d'un fichier d'entrée dans un fichier de sortie
    :param input_audio_path: path fichier d'entrée
    :param output_audio_path: path fichier de sortie
    :param multiplier: facteur
    """
    # Charger la piste audio
    audio = AudioSegment.from_file(input_audio_path)

    # Multiplier la piste audio par le facteur
    multiplied_audio = audio * int(multiplier)

    # Écrire la piste audio multipliée dans un fichier
    multiplied_audio.export(output_audio_path, format="mp3")
    print("multiply_and_write_audio done !")


def merge_audio(audio1_path, audio2_path, output_mp3_path):
    sound1 = AudioSegment.from_file(audio1_path, format="mp3")
    sound2 = AudioSegment.from_file(audio2_path, format="mp3")

    # normalize
    if sound1.dBFS > sound2.dBFS:
        overlay = sound2.overlay(sound1 - (sound1.dBFS - sound2.dBFS // 1.5), position=0)
    else:
        overlay = sound1.overlay(sound2 - (sound2.dBFS - sound1.dBFS // 1.5), position=0)

    overlay.export(output_mp3_path, format="mp3")


def mix_audio_and_export(video_path, audio_path):
    """
    fusionne la piste audio de la vidéo avec celle en deuxième param
    :param video_path: path piste vidéo
    :param audio_path: path piste audio
    :return path audio de sortie
    """
    try:
        output_mp3_path = os.path.splitext(video_path)[0] + "__mix_sound.mp3"

        # Charger la vidéo
        video_clip = VideoFileClip(video_path)

        # Charger les pistes audio
        audio_clip_video = AudioFileClip(video_path)
        audio_clip_from_audiofile = AudioFileClip(audio_path)

        # Adapter la durée de la piste audio externe
        if audio_clip_from_audiofile.duration <= audio_clip_video.duration:
            # Si la piste audio externe est plus courte, la multiplier
            mul = audio_clip_video.duration // audio_clip_from_audiofile.duration + 1
            audio_clip_from_audiofile.close()
            multiply_and_write_audio(audio_path, audio_path, mul)
            audio_clip_from_audiofile = AudioFileClip(audio_path)

        # la piste audio externe est plus longue, donc on la tronque
        audio_clip_from_audiofile = audio_clip_from_audiofile.subclip(0, audio_clip_video.duration)

        # Superposer les pistes audio
        audio_clip_video.set_duration(video_clip.duration)
        audio_clip_from_audiofile.set_duration(video_clip.duration)

        # merge audioclip
        audio_clip_video.write_audiofile(video_path + ".mp3", codec='mp3')
        audio_clip_from_audiofile.write_audiofile(audio_path + ".mp3", codec='mp3')

        # Exporter le mélange audio au format MP3
        merge_audio(video_path + ".mp3", audio_path + ".mp3", output_mp3_path)

        # Fermer les clips
        video_clip.close()
        audio_clip_video.close()
        audio_clip_from_audiofile.close()

        os.remove(video_path + ".mp3")
        os.remove(audio_path + ".mp3")

        return output_mp3_path

    except Exception as e:
        print(f"Erreur lors du mélange audio et de l'export : {str(e)}")

def get_audio_duration(audio_path):
    """
    :param audio_path: chemin absolu du fichier audio
    :return: durée du fichier audio en secondes
    """
    # Commande FFmpeg pour obtenir la durée de l'audio
    ffmpeg_command = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_path}"'

    # Exécution de la commande FFmpeg
    duration_info = os.popen(ffmpeg_command).read().strip()

    # Conversion de la durée en float
    duration = float(duration_info)

    return duration


def audio_replace(video_path, audio_path):
    """
    replace audio with compression
    :param video_path:
    :param audio_path:
    :return:
    """
    # Vérifier la durée de l'audio
    if get_audio_duration(audio_path) < get_video_duration(video_path):
        multiply_and_write_audio(audio_path, audio_path, 2)

    output_path = os.path.splitext(video_path)[0] + "__new_audio.mp4"

    ffmpeg_command = (
        f'ffmpeg -i "{video_path}" -i "{audio_path}" -c:v h264_nvenc -c:a aac -strict experimental '
        f'-b:v 8000k -b:a 192k -map 0:v:0 -map 1:a -shortest "{output_path}"'
    )
    os.system(ffmpeg_command)


def audio_combine(video_path, audio_path):
    """
    combine un fichier vidéo avec un fichier audio
    :param video_path: path fichier vidéo
    :param audio_path: path fichier audio
    """
    new_audio_path = mix_audio_and_export(video_path, audio_path)
    audio_replace(video_path, new_audio_path)
    os.remove(new_audio_path)

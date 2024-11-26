import os
from pydub import AudioSegment
from moviepy.editor import VideoFileClip, AudioFileClip

from file_manipulation.video_modif import get_video_duration
from thread import exec


def apply_reverb(input_path:str)->str:
    """
    add reverb to a copy of input file
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} don't exist")
    
    reverb_parameters = "0.8:0.9:1000:0.6"
    output_path = os.path.splitext(input_path)[0] + "__reverb.mp3"

    ffmpeg_command = (
        f'ffmpeg -y -i "{input_path}" -af "aecho={reverb_parameters}" -c:a libmp3lame -q:a 2 "{output_path}"'
    )
    exec(ffmpeg_command)

    return output_path


def apply_deep_voice(input_path:str, sampling_rate:float=0.8)->str:
    """
    add deep effect to a copy of input file
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} don't exist")
    if sampling_rate <= 0 or sampling_rate > 1:
        raise Exception(f"invalid sampling rate: {sampling_rate}")
    
    output_path = os.path.splitext(input_path)[0] + f"__deep{sampling_rate}.mp3"

    ffmpeg_command = (
        f'ffmpeg -y -i "{input_path}" -af "asetrate={sampling_rate}*44100" -c:a libmp3lame -q:a 2 "{output_path}"'
    )

    exec(ffmpeg_command)

    return output_path


def multiply_audio(input_audio_path:str, output_audio_path:str, multiplier:int)->None:
    """
    multiply an audio in a new file, overwrite if same name
    :param multiplier: facteur
    """
    audio = AudioSegment.from_file(input_audio_path)

    multiplied_audio = audio * int(multiplier)

    multiplied_audio.export(output_audio_path, format="mp3")
    
    print("multiply_audio done !")


def merge_audio(audio1_path:str, audio2_path:str, output_mp3_path:str)->None:
    sound1 = AudioSegment.from_file(audio1_path, format="mp3")
    sound2 = AudioSegment.from_file(audio2_path, format="mp3")

    # normalize
    if sound1.dBFS > sound2.dBFS:
        overlay = sound2.overlay(sound1 - (sound1.dBFS - sound2.dBFS // 1.5), position=0)
    else:
        overlay = sound1.overlay(sound2 - (sound2.dBFS - sound1.dBFS // 1.5), position=0)

    overlay.export(output_mp3_path, format="mp3")


def mix_audio_and_export(video_path:str, audio_path:str)->str:
    """
    merge audio in video
    :param video_path: path piste vidéo
    :param audio_path: path piste audio
    :return path audio de sortie
    """
    output_mp3_path = os.path.splitext(video_path)[0] + "__mix_sound.mp3"

    video_clip = VideoFileClip(video_path)

    audio_clip_video = AudioFileClip(video_path)
    audio_clip_from_audiofile = AudioFileClip(audio_path)

    # multiply audio if shorter
    if audio_clip_from_audiofile.duration <= audio_clip_video.duration:
        mul = audio_clip_video.duration // audio_clip_from_audiofile.duration + 1
        audio_clip_from_audiofile.close()
        multiply_audio(audio_path, audio_path, mul)
        audio_clip_from_audiofile = AudioFileClip(audio_path)

    # troncate audio file if longer
    audio_clip_from_audiofile = audio_clip_from_audiofile.subclip(0, audio_clip_video.duration)

    # cut to video duration
    audio_clip_video.set_duration(video_clip.duration)
    audio_clip_from_audiofile.set_duration(video_clip.duration)

    # merge audioclip
    audio_clip_video.write_audiofile(video_path + ".mp3", codec='mp3')
    audio_clip_from_audiofile.write_audiofile(audio_path + ".mp3", codec='mp3')

    # create new audio
    merge_audio(video_path + ".mp3", audio_path + ".mp3", output_mp3_path)

    video_clip.close()
    audio_clip_video.close()
    audio_clip_from_audiofile.close()

    os.remove(video_path + ".mp3")
    os.remove(audio_path + ".mp3")

    return output_mp3_path

def get_audio_duration(audio_path:str)->float:
    """
    :param audio_path: chemin absolu du fichier audio
    :return: durée du fichier audio en secondes
    """
    ffmpeg_command = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_path}"'

    duration_info = os.popen(ffmpeg_command).read().strip()

    return float(duration_info)


def audio_replace(video_path:str, audio_path:str, name_add:str="__replace.mp4", compress:bool=True)->str:
    """
    replace audio
    :param video_path:
    :param audio_path:
    :return:
    """
    # need audio duration gt video
    if get_audio_duration(audio_path) < get_video_duration(video_path):
        multiply_audio(audio_path, audio_path, 2)

    output_path = os.path.splitext(video_path)[0] + name_add

    if compress:
        ffmpeg_command = (
            f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v h264_nvenc -c:a aac -strict experimental '
            f'-b:v 8000k -b:a 192k -map 0:v:0 -map 1:a -shortest "{output_path}"'
        )
    else:
        ffmpeg_command = (
            f'ffmpeg -y -i "{video_path}" -i "{audio_path}" -c:v h264_nvenc -c:a aac -strict experimental '
            f'-map 0:v:0 -map 1:a -shortest "{output_path}"'
        )
    exec(ffmpeg_command)
    return output_path


def audio_combine(video_path:str, audio_path:str, compress:bool=True)->str:
    """
    combine video file with audio file
    """
    new_audio_path = mix_audio_and_export(video_path, audio_path)
    output_path = audio_replace(video_path, new_audio_path, "__combine.mp4", compress)
    os.remove(new_audio_path)
    return output_path

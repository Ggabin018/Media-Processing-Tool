import logging
import shutil
import tempfile
from math import ceil

import ffmpeg
import os
import json
import subprocess

from moviepy.editor import VideoFileClip, AudioFileClip

from file_manipulation.video_modif import get_video_duration
from toolbox.thread_processing import exec_command


def get_audio_duration(audio_path: str) -> float:
    """
    :param audio_path: chemin absolu du fichier audio
    :return: durée du fichier audio en secondes
    """
    ffmpeg_command = f'ffprobe -v error -show_entries format=duration -of csv=p=0 "{audio_path}"'

    duration_info = os.popen(ffmpeg_command).read().strip()

    return float(duration_info)


def get_loudness(file_path):
    """Get the integrated loudness of an audio file"""
    try:
        # Create and compile the ffmpeg command with loudnorm filter
        args = (
            ffmpeg
            .input(file_path)
            .filter_('loudnorm', print_format='json', i=-24, lra=7, tp=-2)
            .output('-', format='null')
            .compile()
        )

        # Add -hide_banner to reduce output noise
        args.insert(1, '-hide_banner')

        # Run the command and capture output
        process = subprocess.run(
            args,
            stderr=subprocess.PIPE,
            text=True
        )

        # Extract JSON from stderr - it's at the end after "[Parsed_loudnorm_0 @ ...]"
        stderr = process.stderr
        json_match = stderr.rfind('{\n')  # Find the start of the JSON block

        if json_match >= 0:
            json_text = stderr[json_match:]  # Extract everything from the JSON start to the end
            loudness_info = json.loads(json_text)
            return float(loudness_info.get('input_i', -24.0))

        logging.WARN("JSON block not found")
        return -24.0

    except (ffmpeg.Error, json.JSONDecodeError, ValueError, IndexError) as e:
        logging.ERROR(f"Error: {e}")
        return -24.0


def apply_reverb(input_path: str) -> str:
    """
    add reverb to a copy of input file
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} doesn't exist")

    # format: "in_gain:out_gain:delays:decays"
    reverb_parameters = "0.8:0.9:1000:0.6"
    output_path = os.path.splitext(input_path)[0] + "__reverb.mp3"

    input_stream = ffmpeg.input(input_path)

    audio = input_stream.audio.filter("aecho", reverb_parameters)

    output = ffmpeg.output(
        audio,
        output_path,
        acodec='libmp3lame',
        aq=2
    )

    output = output.overwrite_output()
    ffmpeg.run(output)

    return output_path


def apply_deep_voice(input_path: str, sampling_rate: float = 0.8) -> str:
    """
    add deep effect to a copy of input file
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} doesn't exist")
    if sampling_rate <= 0 or sampling_rate > 1:
        raise Exception(f"invalid sampling rate: {sampling_rate}")

    output_path = os.path.splitext(input_path)[0] + f"__deep{sampling_rate}.mp3"

    input_stream = ffmpeg.input(input_path)

    # asetrate filter to lower the pitch
    audio = input_stream.audio.filter("asetrate", f"{sampling_rate}*44100")

    output = ffmpeg.output(
        audio,
        output_path,
        acodec='libmp3lame',
        aq=2
    )

    output = output.overwrite_output()
    ffmpeg.run(output)

    return output_path


def multiply_audio(input_audio_path: str, output_audio_path: str, multiplier: int) -> None:
    """
    Multiply an audio file by concatenating it multiple times, using only ffmpeg
    :param input_audio_path: Path to the input audio file
    :param output_audio_path: Path to write the output audio file
    :param multiplier: Number of times to repeat the audio
    """
    if not os.path.exists(input_audio_path):
        raise Exception(f"{input_audio_path} doesn't exist")

    if multiplier <= 0:
        raise Exception(f"Invalid multiplier: {multiplier}")

    if multiplier == 1:
        shutil.copy(input_audio_path, output_audio_path)
        print("multiply_audio done!")
        return

    # avoid Impossible to open file on same file
    temp_input_path = ""
    if input_audio_path == output_audio_path:
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_audio:
            temp_input_path = temp_audio.name
            shutil.copy(input_audio_path, temp_input_path)
    if temp_input_path:
        input_audio_path = temp_input_path
        
    # temporary text file for concat demuxer
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as temp_file:
        for _ in range(multiplier):
            temp_file.write(f"file '{os.path.abspath(input_audio_path)}'\n")
        temp_file_path = temp_file.name

    try:
        # concat demuxer
        (ffmpeg
         .input(temp_file_path, format='concat', safe=0)
         .output(output_audio_path, c='copy')
         .overwrite_output()
         .run())
    finally:
        os.unlink(temp_file_path)
        if temp_input_path:
            os.unlink(temp_input_path)


def merge_audio(audio1_path: str, audio2_path: str, output_mp3_path: str) -> None:
    """
    Only merge two audio files with automatic normalization
    """
    if not os.path.exists(audio1_path):
        raise Exception(f"{audio1_path} doesn't exist")
    if not os.path.exists(audio2_path):
        raise Exception(f"{audio2_path} doesn't exist")

    loudness1 = get_loudness(audio1_path)
    loudness2 = get_loudness(audio2_path)

    # Calculate volume adjustment
    if loudness1 > loudness2:
        vol1 = (loudness1 - loudness2) / 1.5
        vol2 = 0
    else:
        vol1 = 0
        vol2 = (loudness2 - loudness1) / 1.5

    filter_complex = (
        f"[0:a]volume={-vol1}dB[a1];"
        f"[1:a]volume={-vol2}dB[a2];"
        f"[a1][a2]amix=inputs=2:duration=longest"
    )

    input1 = ffmpeg.input(audio1_path)
    input2 = ffmpeg.input(audio2_path)

    ffmpeg.output(input1, input2,
             output_mp3_path,
             acodec='libmp3lame',
             filter_complex=filter_complex
            ).overwrite_output().run()


def mix_audio_and_export(video_path: str, audio_path: str) -> str:
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


def audio_replace(video_path: str, audio_path: str, name_add: str = "__replace.mp4", compress: bool = False) -> str:
    """
    replace audio, compress possible
    :param video_path: path to input video file
    :param audio_path: path to input audio file
    :param name_add: suffix to add to output filename
    :param compress: whether to compress the output video
    :return: path to output video file
    """
    audio_duration = get_audio_duration(audio_path)
    video_duration = get_video_duration(video_path)
    # need audio duration -gt video
    if audio_duration < video_duration:
        multiply_audio(audio_path, audio_path, ceil(video_duration/audio_duration))

    output_path = os.path.splitext(video_path)[0] + name_add

    video_input = ffmpeg.input(video_path, hwaccel='cuda')
    audio_input = ffmpeg.input(audio_path)

    video_stream = video_input.video
    audio_stream = audio_input.audio

    # Set up output options
    output_args = {
        'c:v': 'hevc_nvenc',
        'c:a': 'copy',
        'strict': 'experimental',
        'shortest': None
    }

    if compress:
        output_args.update({
            'b:v': '8000k',
            'b:a': '192k'
        })

    ffmpeg.output(
        video_stream,
        audio_stream,
        output_path,
        **output_args
    ).overwrite_output().run()

    return output_path


def audio_combine(video_path: str, audio_path: str, compress: bool = True) -> str:
    """
    combine video file with audio file
    """
    new_audio_path = mix_audio_and_export(video_path, audio_path)
    output_path = audio_replace(video_path, new_audio_path, "__combine.mp4", compress)
    os.remove(new_audio_path)
    return output_path


if __name__ == "__main__":
    v_path = "/home/gabin/Media-Processing-Tool/tests/videos/test.mp4"
    a_path = "/home/gabin/Media-Processing-Tool/tests/audios/sample1.mp3"
    o_path = "/home/gabin/Media-Processing-Tool/tests/audios/test__merge.mp3"
    audio_replace(v_path, a_path)

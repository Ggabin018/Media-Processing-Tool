import logging
import shutil
import tempfile
import ffmpeg
import os
import json
import subprocess

from math import ceil
from file_manipulation.video_manip import get_video_duration


def is_audio(path: str):
    _, ext = os.path.splitext(path)
    return ext in [".mp3", ".wav", ".ogg", ".flac"]


def get_audio_duration(audio_path: str) -> float | str:
    """
    :param audio_path: path to audio
    :return: audio duration
    """
    if not is_audio(audio_path):
        return f"Error: Not a audio file"
    try:
        probe = ffmpeg.probe(audio_path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}"
    except KeyError:
        return "Could not find duration information in the video file"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def get_loudness(file_path):
    """Get the integrated loudness of an audio file"""
    json_text = ""
    try:
        # loudnorm filter
        args = (
            ffmpeg
            .input(file_path)
            .filter_('loudnorm', print_format='json', i=-24, lra=7, tp=-2)
            .output('-', format='null')
            .compile()
        )

        # reduce output noise
        args.insert(1, '-hide_banner')

        process = subprocess.run(
            args,
            stderr=subprocess.PIPE,
            text=True
        )

        # Extract JSON from stderr after "[Parsed_loudnorm_0 @ ...]"
        stderr = process.stderr
        json_match_start = stderr.rfind('{\n')
        json_match_end = stderr.rfind('}\n')
        if 0 <= json_match_start < json_match_end:
            json_text = stderr[json_match_start:json_match_end + 1]
            loudness_info = json.loads(json_text)
            return float(loudness_info.get('input_i', -24.0))

        logging.error("Error: get_loudness -> returning default value")

    except ffmpeg.Error as e:
        logging.error(f"Error(get_loudness): ffmpeg: {e}")
    except json.JSONDecodeError as e:
        logging.error(f"Error(get_loudness): json: {e}\n{json_text}\n")
    except (ValueError, IndexError) as e:
        logging.error(f"Error(get_loudness): ValueError or IndexError: {e}\n{json_text}\n")
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
    Merge audio in video using ffmpeg
    :param video_path: path to video file
    :param audio_path: path to audio file
    :return: path to output mixed audio file
    """
    output_mp3_path = os.path.splitext(video_path)[0] + "__mix_sound.mp3"

    # Get durations
    video_duration = get_video_duration(video_path)
    audio_duration = get_audio_duration(audio_path)

    if isinstance(video_duration, str):
        raise Exception(f"Video duration error: {video_duration}")
    if isinstance(audio_duration, str):
        raise Exception(f"Audio duration error: {audio_duration}")

    # Extract audio from video and convert to consistent format
    video_audio_path = os.path.splitext(video_path)[0] + "__video_audio.wav"
    (
        ffmpeg.input(video_path)
        .output(video_audio_path, acodec='pcm_s16le', ar=44100, ac=2)
        .overwrite_output()
        .run()
    )

    # Convert input audio to same format if needed
    converted_audio_path = os.path.splitext(audio_path)[0] + "__converted.wav"
    (
        ffmpeg.input(audio_path)
        .output(converted_audio_path, acodec='pcm_s16le', ar=44100, ac=2)
        .overwrite_output()
        .run()
    )
    audio_path = converted_audio_path

    # Multiply audio if shorter than video
    temp_audio_path = None
    if audio_duration < video_duration:
        multiplier = ceil(video_duration / audio_duration)
        temp_audio_path = os.path.splitext(audio_path)[0] + "__temp.wav"
        multiply_audio(audio_path, temp_audio_path, multiplier)
        audio_path = temp_audio_path

    try:
        # Mix the two audio files
        # I: Target integrated loudness
        # TP: True peak limit
        # LRA=11: Loudness range target
        (
            ffmpeg.filter([
                ffmpeg.input(video_audio_path),
                ffmpeg.input(audio_path)
            ], 'amix', inputs=2, duration='shortest')
            .filter('loudnorm', I=-16, TP=-1.5, LRA=11)
            .output(output_mp3_path, acodec='libmp3lame', ar=44100, ac=2, audio_bitrate='192k')
            .overwrite_output()
            .run()
        )

        # Ensure the mixed audio matches video duration
        mixed_duration = get_audio_duration(output_mp3_path)
        if mixed_duration > video_duration:
            temp_output = output_mp3_path + ".tmp.mp3"
            (
                ffmpeg.input(output_mp3_path)
                .output(temp_output, acodec='libmp3lame', t=video_duration)
                .overwrite_output()
                .run()
            )
            os.replace(temp_output, output_mp3_path)

    finally:
        # Clean up temporary files
        for temp_file in [video_audio_path, converted_audio_path, temp_audio_path]:
            if temp_file and os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                except:
                    pass

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
    if type(video_duration) == str:
        return video_duration

    # need audio duration -gt video
    if audio_duration < video_duration:
        multiply_audio(audio_path, audio_path, ceil(video_duration / audio_duration))

    output_path = os.path.splitext(video_path)[0] + name_add

    video_input = ffmpeg.input(video_path, hwaccel='cuda')
    audio_input = ffmpeg.input(audio_path)

    video_stream = video_input.video
    audio_stream = audio_input.audio

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

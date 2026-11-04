import os
import shutil

import ffmpeg

from toolbox.ffmpeg_runner import run_ffmpeg
from toolbox.progress import run_task
from toolbox.utils import to_seconds


def _duration_or_none(video_path: str) -> float | None:
    duration = get_video_duration(video_path)
    return duration if isinstance(duration, float) else None


def is_video(path: str) -> bool:
    _, file_extension = os.path.splitext(path)
    return file_extension in [".mp4", ".mov", ".avi", ".webm", ".mkv"]


def get_original_codecs(input_video) -> tuple[str, str]:
    """Get the video and audio codecs of the input video file"""
    if not is_video(input_video):
        return f"Error: Not a video file", ""
    try:
        probe = ffmpeg.probe(input_video, v='error', select_streams='v:0', show_entries='stream=codec_name')
        video_codec = probe['streams'][0]['codec_name']

        probe = ffmpeg.probe(input_video, v='error', select_streams='a:0', show_entries='stream=codec_name')
        audio_codec = probe['streams'][0]['codec_name']

        return video_codec, audio_codec
    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}", ""


def get_video_duration(video_path: str) -> float | str:
    """
    :param video_path: chemin absolu de la vidéo
    :return: durée de la vidéo en secondes
    """
    if not is_video(video_path):
        return f"Error: Not a video file"
    try:
        probe = ffmpeg.probe(video_path)

        duration = float(probe['format']['duration'])

        return duration
    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}"
    except KeyError:
        return "Could not find duration information in the video file"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def get_resolution(video_path: str) -> tuple[int | str, int | None]:
    """
    Get the resolution (width and height) of a video file using ffmpeg-python
    
    :param video_path: absolute path to the video file
    :return: tuple of (width, height) in pixels
    """
    if not is_video(video_path):
        return f"Error: Not a video file", None
    try:
        probe = ffmpeg.probe(video_path)

        video_stream = next((stream for stream in probe['streams']
                             if stream['codec_type'] == 'video'), None)

        if video_stream is None:
            raise ValueError("No video stream found in the file")

        width = int(video_stream['width'])
        height = int(video_stream['height'])

        return width, height
    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}", None
    except (KeyError, ValueError) as e:
        return f"Error extracting resolution: {e}", None


def get_video_bitrate(video_path: str) -> float | str:
    """
    Get video bitrate in kbps using ffmpeg-python
    
    :param video_path: Absolute path to the video file
    :return: Bitrate of the video in kbps
    """
    if not is_video(video_path):
        return f"Error: Not a video file"
    try:
        probe = ffmpeg.probe(video_path)

        video_stream = next((stream for stream in probe['streams']
                             if stream['codec_type'] == 'video'), None)

        if video_stream is None:
            raise ValueError("No video stream found in the file")

        if 'bit_rate' in video_stream and video_stream['bit_rate']:
            bitrate = float(video_stream['bit_rate'])
        elif 'bit_rate' in probe['format'] and probe['format']['bit_rate']:
            bitrate = float(probe['format']['bit_rate'])
        else:
            raise ValueError("Bitrate information not found")

        return bitrate / 1000

    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}"
    except (KeyError, ValueError) as e:
        return f"Error extracting bitrate: {e}"


def video_cut(input_video: str, start=None, end=None, output_video: str | None = None) -> str:
    """
    Cut a video from start to end
    :param input_video: path to the input video file
    :param start: start time in format "HH:MM:SS" or seconds
    :param end: end time in format "HH:MM:SS" or seconds
    :param output_video: output path (default: <input>__cut.mp4)
    :return: path to the output video file
    """
    if not is_video(input_video):
        return f"Error: Not a video file"

    if start:
        tmp = to_seconds(start)
        if tmp is None:
            return f"Syntax error: Start Time: {start}, expected HH:MM:SS or seconds"
        start = tmp
    if end:
        tmp = to_seconds(end)
        if tmp is None:
            return f"Syntax error: End Time: {end}, expected HH:MM:SS or seconds"
        end = tmp

    if start and end:
        if start >= end:
            return f"Error: Start Time ({start}) >= End Time ({end})"

    output_video = output_video or os.path.splitext(input_video)[0] + "__cut.mp4"

    try:
        if start:
            stream = ffmpeg.input(input_video, ss=start)
        else:
            stream = ffmpeg.input(input_video)
        if end:
            duration = (end - start) if start else end
            stream = ffmpeg.output(stream, output_video, t=duration, c="copy")
        else:
            stream = ffmpeg.output(stream, output_video, c="copy")

        output = ffmpeg.overwrite_output(stream)

        if end:
            expected = end - (start or 0)
        else:
            total = _duration_or_none(input_video)
            expected = total - (start or 0) if total else None
        run_ffmpeg(output, duration=expected, desc=f"Cut {os.path.basename(input_video)}")

        return output_video

    except Exception as e:
        return f"Error: {e}"


def video_upscale(input_video: str, factor: int) -> str:
    """
    Multiply the resolution of a video

    :param input_video: path to the input video file
    :param factor: multiplier for resolution (e.g., 2 for doubling)
    :return: path to the output video file
    """
    if not is_video(input_video):
        return f"Error: Not a video file"

    output_video = os.path.splitext(input_video)[0] + f"__up{factor}.mp4"

    try:
        stream = ffmpeg.input(input_video)

        video = (
            stream.video
            .filter('scale', f'iw*{factor}', f'ih*{factor}')
            .filter('unsharp', '5:5:1.0:5:5:0.0')
            .filter('hqdn3d',
                    luma_spatial=4,
                    chroma_spatial=4,
                    luma_tmp=4,
                    chroma_tmp=4)
        )

        audio = stream.audio

        output = ffmpeg.output(video, audio, output_video, acodec='copy')
        output = ffmpeg.overwrite_output(output)

        run_ffmpeg(output, duration=_duration_or_none(input_video), desc=f"Upscale {os.path.basename(input_video)}")

        return output_video

    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"
    except Exception as e:
        return f"Error during video upscaling: {str(e)}"


def video_compress(video_path: str, output_filename: str = "", target_bitrate: int = 8000,
                   min_resolution: int = 1080, vcodec: str = "hevc_nvenc") -> str:
    """
    Convert video to 1080p with CUDA acceleration while keeping aspect ratio

    :param video_path: path to the input video file
    :param output_filename: path for output file, if not specified adds __compressed to filename
    :param target_bitrate: target bitrate in kbps (default: 8000)
    :param min_resolution: minimum resolution
    :return: path to the output video file or original path if no compression needed
    """
    if not is_video(video_path):
        return f"Error: Not a video file"

    target_bitrate = int(target_bitrate)
    duration = get_video_duration(video_path)
    if type(duration) == str:
        return duration

    try:
        width, height = get_resolution(video_path)
        if height is None:
            return width

        # adjust resolution + avoid upscale
        min_resolution = min(width, height, min_resolution)

        # Check if compression is needed
        if output_filename == "":
            output_filename = os.path.splitext(video_path)[0] + f"__compressed.mp4"

        # CUDA acceleration
        input_stream = ffmpeg.input(video_path, hwaccel='cuda')

        # scaling based on orientation
        if width > height:
            video = input_stream.video.filter('scale', -2, min_resolution)
        else:
            video = input_stream.video.filter('scale', min_resolution, -2)

        audio = input_stream.audio

        output = ffmpeg.output(
            video,
            audio,
            output_filename,
            vcodec=vcodec,
            video_bitrate=f'{target_bitrate}k',
            acodec='copy',
            pix_fmt='yuv420p',
        )

        output = ffmpeg.overwrite_output(output)

        run_ffmpeg(output, duration=duration, desc=f"Compress {os.path.basename(video_path)}")
        return output_filename

    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


def videos_concat(videos: list[str], output_video: str | None = None) -> str:
    """
    Concatenate multiple video files using FFmpeg's concat protocol

    This method is especially useful for concatenating files with different codecs.

    :param videos: list of video paths
    :param output_video: output path (default: <first video>__concat.mp4)
    :return: path to the output concatenated video file
    """
    if not videos or len(videos) < 2:
        return "Error: At least two videos are required for concatenation"

    output_video = output_video or os.path.splitext(videos[0])[0] + "__concat.mp4"

    try:
        # Create intermediate inputs
        inputs = [ffmpeg.input(video) for video in videos]

        # Create separate video and audio streams for each input
        video_streams = [input.video for input in inputs]
        audio_streams = [input.audio for input in inputs]

        # Concatenate streams
        joined_video = ffmpeg.concat(*video_streams, v=1, a=0)
        joined_audio = ffmpeg.concat(*audio_streams, v=0, a=1)

        # Combine back and output
        output = ffmpeg.output(joined_video, joined_audio, output_video,
                               vcodec="libx264", acodec="aac", video_bitrate=f"{get_video_bitrate(videos[0])}k" ,audio_bitrate="192K")
        output = ffmpeg.overwrite_output(output)

        durations = [_duration_or_none(v) for v in videos]
        expected = sum(durations) if all(durations) else None
        run_ffmpeg(output, duration=expected, desc=f"Concat {len(videos)} videos")
        return output_video

    except Exception as e:
        return f"Error: {str(e)}"


END_TOLERANCE = 0.5  # seconds: an end typed as the rounded duration is accepted


def _hms(seconds: float) -> str:
    seconds = int(seconds)
    return f"{seconds // 3600:02d}:{seconds % 3600 // 60:02d}:{seconds % 60:02d}"


def validate_segments(times: list[tuple[str | None, str | None]], duration: float | None) -> list[str]:
    """
    Check every segment before cutting anything: one message per problem, all at once.
    Order and overlaps are not checked (segments can be reordered on purpose).
    An empty end is allowed only for the last segment (until the end of the video).
    :param duration: video duration in seconds, None to skip the checks against it
    """
    errors = []
    for i, (start, end) in enumerate(times, start=1):
        start_s = to_seconds(start) if start not in (None, "") else None
        if start in (None, ""):
            errors.append(f"segment {i}: missing start")
        elif start_s is None:
            errors.append(f"segment {i}: invalid start {start!r}")

        end_s = None
        if end in (None, ""):
            if i != len(times):
                errors.append(f"segment {i}: missing end (only the last segment can go to the end of the video)")
        else:
            end_s = to_seconds(end)
            if end_s is None:
                errors.append(f"segment {i}: invalid end {end!r}")

        if start_s is not None and end_s is not None and start_s >= end_s:
            errors.append(f"segment {i}: start {_hms(start_s)} >= end {_hms(end_s)}")
        if duration:
            if start_s is not None and start_s >= duration:
                errors.append(f"segment {i}: start {_hms(start_s)} is after the end of the video ({_hms(duration)})")
            if end_s is not None and end_s > duration + END_TOLERANCE:
                errors.append(f"segment {i}: end {_hms(end_s)} is after the end of the video ({_hms(duration)})")
    return errors


def multiple_cuts_plus_concatenate(video_path: str, times: list[tuple[str, str | None]]) -> str:
    """
    Cut every segment next to the video (<video>__cut__<i>.mp4, kept for later edits),
    then join them into <video>__concat.mp4. Nothing is cut if one segment is invalid.
    """
    errors = validate_segments(times, _duration_or_none(video_path))
    if errors:
        return "Error: invalid segments\n" + "\n".join(errors)

    base = os.path.splitext(video_path)[0]
    final = base + "__concat.mp4"
    n = len(times)
    padding = len(str(n))
    segments = []
    for i, (start, end) in enumerate(times):
        segment = f"{base}__cut__{i:0{padding}}.mp4"
        # one line per step on the progress board
        path = run_task(f"segment {i + 1}/{n}", video_cut, video_path, start, end, output_video=segment)
        if not os.path.isfile(path):
            return f"Error with parameters: start={start} end={end}: {path}"
        segments.append(path)

    if len(segments) == 1:
        shutil.copyfile(segments[0], final)  # same name as with several segments
        return final
    return run_task("concaténation", videos_concat, segments, output_video=final)

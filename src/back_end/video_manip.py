import os
import os
import sys
import tempfile

import ffmpeg

from toolbox.ProgressBar import progress_bar
from toolbox.utils import to_seconds


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


def video_cut(input_video: str, start=None, end=None) -> str:
    """
    Cut a video from start to end
    :param input_video: path to the input video file
    :param start: start time in format "HH:MM:SS" or seconds
    :param end: end time in format "HH:MM:SS" or seconds
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

    output_video = os.path.splitext(input_video)[0] + "__cut.mp4"

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

        stream = ffmpeg.overwrite_output(stream)

        ffmpeg.run(stream)

        return output_video

    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}"


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

        ffmpeg.run(output)

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

        # Check if compression is needed
        if width >= min_resolution or height >= min_resolution:
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
                **{'stats': None, 'progress': 'pipe:1'}  # Force progress output
            )

            output = ffmpeg.overwrite_output(output)

            print(f"Compressing {os.path.basename(video_path)} to {os.path.basename(output_filename)}")
            process = ffmpeg.run_async(output, pipe_stdout=True)

            progress_bar(duration, process)

            # Wait for process to finish
            return_code = process.wait()

            if return_code == 0:
                sys.stdout.write("\n")
                print(f"Compression completed successfully")
                return output_filename
            else:
                return f"\nCompression failed with return code {return_code}"
        else:
            return f"{video_path} is already < to {min_resolution}."

    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"


def videos_concat(videos: list[str]) -> str:
    """
    Concatenate multiple video files

    :param videos: list of video paths
    :return: path to the output concatenated video file
    """
    if not videos or len(videos) < 2:
        return "Error: At least two videos are required for concatenation"

    # Check if all files are videos
    for video in videos:
        if not is_video(video):
            return f"Error: {video} is not a video file"

    # Create output filename based on first video
    base_name = os.path.splitext(videos[0])[0]
    output_video = f"{base_name}__concat.mp4"

    try:
        # Create temporary directory for intermediate files
        temp_dir = tempfile.mkdtemp()

        # First pass: normalize all videos to ensure consistent timestamps
        normalized_videos = []

        for i, video in enumerate(videos):
            normalized_path = os.path.join(temp_dir, f"norm_{i}.ts")
            normalized_videos.append(normalized_path)

            # Convert to TS format which helps with timestamp issues
            stream = ffmpeg.input(video)
            output = ffmpeg.output(
                stream,
                normalized_path,
                f='mpegts',  # Use MPEG-TS format which handles timestamps better
                acodec='aac',  # Consistent audio codec
                vcodec='libx264'  # Consistent video codec
            )
            output = ffmpeg.overwrite_output(output)
            ffmpeg.run(output, quiet=False)  # Show output for debugging

        # Second pass: concat using TS inputs (which handle timestamps better)
        inputs = []
        for norm_video in normalized_videos:
            inputs.append(ffmpeg.input(norm_video))

        joined = ffmpeg.concat(*inputs, v=1, a=1)
        output = ffmpeg.output(joined, output_video, f='mp4')
        output = ffmpeg.overwrite_output(output)

        ffmpeg.run(output, quiet=False)  # Show output for debugging

        # Clean up temporary files
        for file in normalized_videos:
            if os.path.exists(file):
                os.unlink(file)
        os.rmdir(temp_dir)

        return output_video

    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e.stderr)
        return f"ffmpeg error: {error_message}"
    except Exception as e:
        return f"Error during video concatenation: {str(e)}"


def multiple_cuts_plus_concatenate(video_path: str, times: list[list[str, str]]) -> str:
    video_paths = []
    padding = len(str(len(times)))
    for i, (start, end) in enumerate(times):
        path = video_cut(video_path, start, end)
        if os.path.exists(path):
            new_name = os.path.splitext(path)[0] + f"__{i:0{padding}}.mp4"
            os.rename(path, new_name)
            video_paths.append(new_name)
        else:
            # error during cut
            return f"Error with parameters:\nstart={start}\nend={end}\n" + path
    return videos_concat(video_paths)

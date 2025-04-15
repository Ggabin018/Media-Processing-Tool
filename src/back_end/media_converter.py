import os
import ffmpeg

from toolbox.ProgressBar import progress_bar

def get_media_duration(path: str) -> float | str:
    """
    :param path: path to audio
    :return: audio duration
    """
    try:
        probe = ffmpeg.probe(path)
        duration = float(probe['format']['duration'])
        return duration
    except ffmpeg.Error as e:
        return f"ffmpeg error: {e.stderr}"
    except KeyError:
        return "Could not find duration information in the video file"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


def convert_media(input_path: str, ext: str) -> str:
    """
    Convert a media file (video or audio) to another format

    Args:
        input_path (str): Path to the input media file
        ext (str): Target extension without dot (e.g. 'mp4', 'webm', 'ogg')

    Returns:
        str: Path to the converted file or error message
    """
    if not os.path.exists(input_path):
        return f"Error: {input_path} doesn't exist"

    duration = get_media_duration(input_path)
    if isinstance(duration, str):  # If duration is an error message
        return duration

    output_path = os.path.splitext(input_path)[0] + "." + ext

    try:
        # Create input
        input_stream = ffmpeg.input(input_path)

        # Set codec options based on output format
        output_args = {}

        # Default video codec based on format
        if ext in ['mp4', 'mkv', 'mov']:
            # Try hardware acceleration first, fall back to software
            try:
                output_args['vcodec'] = 'hevc_nvenc'  # NVIDIA GPU acceleration
            except:
                output_args['vcodec'] = 'libx265'  # Software fallback
        elif ext == 'webm':
            output_args['vcodec'] = 'libvpx-vp9'  # VP9 for WebM
        elif ext == 'ogg':
            output_args['vcodec'] = 'libtheora'  # Theora for Ogg
        elif ext == 'avi':
            output_args['vcodec'] = 'mpeg4'  # MPEG-4 for AVI

        # Default audio codec based on format
        if ext in ['mp4', 'mkv', 'mov', 'avi']:
            output_args['acodec'] = 'aac'
        elif ext == 'webm':
            output_args['acodec'] = 'libopus'
        elif ext == 'ogg':
            output_args['acodec'] = 'libvorbis'

        # Common settings
        output_args['pix_fmt'] = 'yuv420p'  # Standard pixel format

        # Add progress monitoring
        output_args['stats'] = None
        output_args['progress'] = 'pipe:1'

        # Build and run the command
        output = ffmpeg.output(input_stream, output_path, **output_args)
        output = ffmpeg.overwrite_output(output)

        process = ffmpeg.run_async(output, pipe_stdout=True)
        progress_bar(duration, process)
        return_code = process.wait()

        if return_code == 0:
            print(f"\nConversion completed successfully")
            return output_path
        else:
            return f"\nConversion failed with return code {return_code}"

    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if hasattr(e.stderr, 'decode') else str(e.stderr)
        return f"ffmpeg error: {error_message}"
    except Exception as e:
        return f"Error: {str(e)}"

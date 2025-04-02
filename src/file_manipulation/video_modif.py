import os
from src.utils.thread_processing import exec_command
import ffmpeg
import logging

logger = logging.getLogger("video_modif")


def get_video_duration(video_path: str) -> float:
    """
    :param video_path: chemin absolu de la vidéo
    :return: durée de la vidéo en secondes
    """
    try:
        probe = ffmpeg.probe(video_path)

        duration = float(probe['format']['duration'])

        return duration
    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr}")
    except KeyError:
        logger.error("Could not find duration information in the video file")
    return -1


def get_resolution(video_path: str) -> tuple[int, int]:
    """
    Get the resolution (width and height) of a video file using ffmpeg-python
    
    :param video_path: absolute path to the video file
    :return: tuple of (width, height) in pixels
    """
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
        logger.error(f"ffmpeg error: {e.stderr}")
    except (KeyError, ValueError) as e:
        logger.error(f"Error extracting resolution: {e}")
    return -1, -1


def get_video_bitrate(video_path: str) -> float:
    """
    Get video bitrate in kbps using ffmpeg-python
    
    :param video_path: Absolute path to the video file
    :return: Bitrate of the video in kbps
    """
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
        print(f"ffmpeg error: {e.stderr}")
        raise
    except (KeyError, ValueError) as e:
        print(f"Error extracting bitrate: {e}")
        raise


def video_cut(input_video: str, start=None, end=None, fast_flag: bool = True) -> str:
    """
    Cut a video from start to end using ffmpeg-python

    :param input_video: path to the input video file
    :param start: start time in format "HH:MM:SS" or seconds
    :param end: end time in format "HH:MM:SS" or seconds
    :param fast_flag: if True, use faster seeking method (may miss some frames)
    :return: path to the output video file
    """
    output_video = os.path.splitext(input_video)[0] + "__cut.mp4"

    try:
        stream = ffmpeg.input(input_video)

        if fast_flag:
            # Fast seeking method (less accurate but quicker)
            if start is not None and start != "":
                stream = ffmpeg.input(input_video, ss=start)
            if end is not None and end != "":
                stream = stream.to(end)
        else:
            # Slower but more accurate method
            if start is not None and start != "":
                stream = stream.filter('trim', start=start)
            if end is not None and end != "":
                stream = stream.filter('trim', end=end)

        stream = ffmpeg.output(stream, output_video, c='copy')

        stream = ffmpeg.overwrite_output(stream)

        ffmpeg.run(stream, quiet=True)

        return output_video

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr.decode()}")
    return ""


def video_upscale(input_video: str, factor: int) -> str:
    """
    Multiply the resolution of a video

    :param input_video: path to the input video file
    :param factor: multiplier for resolution (e.g., 2 for doubling)
    :return: path to the output video file
    """
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

        ffmpeg.run(output, quiet=True)

        return output_video

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}")
    except Exception as e:
        logger.error(f"Error during video upscaling: {str(e)}")
    return ""

#TODO: add min resolution
def video_compress(video_path: str, output_filename: str = "", target_bitrate: int = 8000) -> str:
    """
    Convert video to 1080p with CUDA acceleration while keeping aspect ratio

    :param video_path: path to the input video file
    :param output_filename: path for output file, if not specified adds __compressed to filename
    :param target_bitrate: target bitrate in kbps (default: 8000)
    :return: path to the output video file or original path if no compression needed
    """
    target_bitrate = int(target_bitrate)

    try:
        width, height = get_resolution(video_path)

        # Check if compression is needed
        if width >= 1080 or height >= 1080:
            if output_filename == "":
                output_filename = os.path.splitext(video_path)[0] + f"__compressed.mp4"

            # CUDA acceleration
            input_stream = ffmpeg.input(video_path, hwaccel='cuda')

            # scaling based on orientation
            if width > height:
                video = input_stream.video.filter('scale', -2, 1080)
            else:
                video = input_stream.video.filter('scale', 1080, -2)

            audio = input_stream.audio

            output = ffmpeg.output(
                video,
                audio,
                output_filename,
                vcodec='hevc_nvenc',
                video_bitrate=f'{target_bitrate}k',
                acodec='copy',
                pix_fmt='yuv420p'  # compatibility
            )

            output = ffmpeg.overwrite_output(output)

            ffmpeg.run(output, quiet=True)

            return output_filename
        else:
            return f"{video_path} is already <= to 1080p."

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}")
    except Exception as e:
        logger.error(f"Failure with {video_path}. Error: {str(e)}")
    return ""


if "__main__" == __name__:
    logging.basicConfig(level=logging.INFO)
    v_path = "/home/gabin/Media-Processing-Tool/ER.mp4"
    if os.path.exists(v_path):
        logger.info("START")

        print("duration:\t", get_video_duration(v_path))
        print("resolution:\t", get_resolution(v_path))
        print("bit_rate:\t", get_video_bitrate(v_path))

        logger.info("END")
    else:
        logger.error("File not found")

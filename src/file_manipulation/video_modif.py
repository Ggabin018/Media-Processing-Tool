import logging
import os
import sys
import ffmpeg

from toolbox.ProgressBar import progress_bar
from toolbox.utils import hhmmss_to_seconds

logger = logging.getLogger("video_modif")


def get_original_codecs(input_video) -> tuple[str, str]:
    """Get the video and audio codecs of the input video file"""
    try:
        probe = ffmpeg.probe(input_video, v='error', select_streams='v:0', show_entries='stream=codec_name')
        video_codec = probe['streams'][0]['codec_name']

        probe = ffmpeg.probe(input_video, v='error', select_streams='a:0', show_entries='stream=codec_name')
        audio_codec = probe['streams'][0]['codec_name']

        return video_codec, audio_codec
    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr}")
    return "", ""


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


def video_cut(input_video: str, start=None, end=None, fast_flag: bool = False) -> str:
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
        if fast_flag:
            # Fast seeking: quick but less precise trimming
            if start:
                stream = ffmpeg.input(input_video, ss=start)
            else:
                stream = ffmpeg.input(input_video)
            if end:
                duration = f"{hhmmss_to_seconds(end) - hhmmss_to_seconds(start)}" if start else end
                stream = ffmpeg.output(stream, output_video, t=duration, c="copy")
            else:
                stream = ffmpeg.output(stream, output_video, c="copy")
        else:
            # Frame-accurate trimming: slower but precise

            stream = ffmpeg.input(input_video, hwaccel='cuda')

            vid = aud = None
            if start and end:
                vid = stream.trim(start=start, end=end).setpts('PTS-STARTPTS')
                aud = stream.filter_('atrim', start=start, end=end).filter_('asetpts', 'PTS-STARTPTS')
            elif start:
                vid = stream.trim(start=start).setpts('PTS-STARTPTS')
                aud = stream.filter_('atrim', start=start).filter_('asetpts', 'PTS-STARTPTS')
            elif end:
                vid = stream.trim(end=end).setpts('PTS-STARTPTS')
                aud = stream.filter_('atrim', end=end).filter_('asetpts', 'PTS-STARTPTS')

            stream = ffmpeg.output(vid, aud, output_video)

        stream = ffmpeg.overwrite_output(stream)

        ffmpeg.run(stream)

        return output_video

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr}")
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

        ffmpeg.run(output)

        return output_video

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}")
    except Exception as e:
        logger.error(f"Error during video upscaling: {str(e)}")
    return ""


# TODO: add min resolution
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
                pix_fmt='yuv420p',
                **{'stats': None, 'progress': 'pipe:1'}  # Force progress output
            )

            output = ffmpeg.overwrite_output(output)

            # Start ffmpeg process
            print(f"Compressing {os.path.basename(video_path)} to {os.path.basename(output_filename)}")
            process = ffmpeg.run_async(output, pipe_stdout=True)

            progress_bar(get_video_duration(video_path), process)

            # Wait for process to finish
            return_code = process.wait()

            if return_code == 0:
                sys.stdout.write("\n")
                print(f"Compression completed successfully")
                return output_filename
            else:
                print(f"\nCompression failed with return code {return_code}")
                return ""
        else:
            return f"{video_path} is already <= to 1080p."

    except ffmpeg.Error as e:
        logger.error(f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}")
    except Exception as e:
        logger.error(f"Failure with {video_path}. Error: {str(e)}")
    return ""




if __name__ == "__main__":
    v_path = "/home/gabin/Media-Processing-Tool/tests/videos/test.mp4"
    # video_cut(v_path, "00:00:30", "00:00:50")
    video_compress(v_path)

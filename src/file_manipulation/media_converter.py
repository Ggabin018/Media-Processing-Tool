import os
import ffmpeg

from toolbox.ProgressBar import progress_bar
from file_manipulation.video_manip import get_video_duration


# FIXME: not working: webm -> Conversion failed!
# FIXME: not working: ogg -> Conversion failed!
# FIXME: not working but: avi -> Conversion failed!
def convert_media(input_path: str, ext: str) -> str:
    """
    Convert a media file (video or audio) to another format
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} doesn't exist")

    duration = get_video_duration(input_path)
    if type(duration) == str:
        return duration

    output_path = os.path.splitext(input_path)[0] + "." + ext

    try:
        input_stream = ffmpeg.input(input_path)

        output = ffmpeg.output(
            input_stream,
            output_path,
            vcodec='hevc_nvenc',
            pix_fmt='yuv420p',
            **{'stats': None, 'progress': 'pipe:1'}  # Force progress output
        )

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
        return f"ffmpeg error: {e.stderr.decode() if hasattr(e.stderr, 'decode') else e.stderr}"
    except Exception as e:
        return f"Error: {str(e)}"

import os
import ffmpeg

from toolbox.ProgressBar import progress_bar
from file_manipulation.video_manip import get_video_duration


# FIXME: not working: webm -> return code error 1
# FIXME: not working: ogg -> return code error 1
# FIXME: working but: mov -> Video does not have browser-compatible container or codec. Converting to mp4.
# FIXME: working but: avi -> Video does not have browser-compatible container or codec. Converting to mp4.
# FIXME: working but: mp4 -> Video does not have browser-compatible container or codec. Converting to mp4.
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

    input_stream = ffmpeg.input(input_path)

    output = ffmpeg.output(
        input_stream,
        output_path,
        vcodec='hevc_nvenc',
        pix_fmt='yuv420p',
        **{'stats': None, 'progress': 'pipe:1'}  # Force progress output
    )

    output = ffmpeg.overwrite_output(output)
    process = ffmpeg.run_async(output, pipe_stdout=True, pipe_stderr=True)

    progress_bar(duration, process)
    return_code = process.wait()

    if return_code == 0:
        print(f"\nConversion completed successfully")
        return output_path
    else:
        print(f"\nConversion failed with return code {return_code}")
        return ""

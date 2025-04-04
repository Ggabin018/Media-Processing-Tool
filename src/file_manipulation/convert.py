import os
import ffmpeg


# TODO: add start_time: int, end_time: int in seconds
def convert_media(input_path: str, ext: str) -> str:
    """
    Convert a media file (video or audio) to another format
    """
    if not os.path.exists(input_path):
        raise Exception(f"{input_path} doesn't exist")

    output_path = os.path.splitext(input_path)[0] + "." + ext

    input_stream = ffmpeg.input(input_path)

    output = ffmpeg.output(input_stream, output_path)

    output.overwrite_output().run()

    return output_path


if __name__ == "__main__":
    path = "/home/gabin/Media-Processing-Tool/tests/videos/test.mp4"
    convert_media(path, "mp3")

import gradio as gr

from file_manipulation.dir_manip import (
    dir_audio_extract,
    dir_audio_replace,
    dir_audio_combine,
    dir_convert_video_to_video,
    dir_compress_videos
)

from file_manipulation.files_manip import (
    files_audio_combine,
    files_audio_replace,
    files_compress_videos,
    files_audio_extract,
    files_convert_video_to_video
)

from file_manipulation.video_modif import (
    video_cut,
    video_compress
)

from file_manipulation.audio_modif import (
    audio_replace,
    audio_combine
)

from file_manipulation.convert import (
    convert_vid2audio,
    convert_vid2vid
)

# use in save
import datetime

from shutil import copy
import os
import tempfile

# use to clean up at the end
import signal
import sys

import tkinter
from tkinter import filedialog

from script_js import js

temp_dir = tempfile.gettempdir()


def regularize_path(path: str) -> str:
    path = path.strip('\'"')
    path = path.replace('\\', '/')
    path = os.path.normpath(path)
    return path


# path of temp file in tempdir
dst_path: str | None = None


def on_close(sig, frame):
    if dst_path is not None:
        os.remove(dst_path)
    sys.exit(0)


signal.signal(signal.SIGINT, on_close)
signal.signal(signal.SIGTERM, on_close)


# region Single File

def on_change_file(src_path: str) -> str:
    global dst_path
    if dst_path is not None and os.path.exists(dst_path):
        os.remove(dst_path)
    dst_path = os.path.join(temp_dir, os.path.basename(src_path))
    return copy(src_path, dst_path)


def cut_video(video_path: str, start, end) -> tuple[str, str]:
    video_path = regularize_path(video_path)
    if not os.path.exists(video_path):
        raise Exception(f"{video_path} does not exit")

    path = video_cut(video_path, start=start, end=end)
    return path, on_change_file(path)


def convert_video_to_mp3(video_path: str) -> tuple[str, str | None]:
    try:
        path = convert_vid2audio(regularize_path(video_path))
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}", None


def convert_video_to_video(video_path: str, ext: str) -> str:
    try:
        return convert_vid2vid(regularize_path(video_path), ext)
    except Exception as e:
        return f"Error: {str(e)}"


def modify_audio(video_path: str, audio_path: str, opt: str = "replace") -> tuple[str, str | None]:
    try:
        if opt == "replace":
            path = audio_replace(regularize_path(video_path), regularize_path(audio_path))
        else:
            path = audio_combine(regularize_path(video_path), regularize_path(audio_path))
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}", None


def compress_vid(video_path: str, bitrate: int = 8000):
    try:
        dir_path = os.path.split(video_path)[0]
        output_folder = os.path.join(dir_path, "output")
        os.makedirs(output_folder, exist_ok=True)
        return video_compress(video_path, target_bitrate=bitrate)
    except Exception as e:
        return f"Error: {str(e)}", None


# endregion

# region Directory

def directory_extract_audio(video_dir_path: str) -> str:
    try:
        return dir_audio_extract(regularize_path(video_dir_path))
    except Exception as e:
        return f"Error: {str(e)}"


def directory_audio_modify(video_dir_path: str, audio_dir_path: str, opt: str = "replace") -> str:
    try:
        if opt == "replace":
            return dir_audio_replace(video_dir_path, audio_dir_path)
        return dir_audio_combine(video_dir_path, audio_dir_path)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_convert(dir_path: str, ext: str) -> str:
    try:
        return dir_convert_video_to_video(dir_path, ext)
    except Exception as e:
        return f"Error: {str(e)}"


def directory_compress(dir_path: str, bitrate: int = 8000):
    try:
        return dir_compress_videos(dir_path, bitrate)
    except Exception as e:
        return f"Error: {str(e)}", None


# endregion

# region Multiples Files

def batch_convert_video_to_video(videos: list[str], ext: str) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        path = files_convert_video_to_video(videos, ext)
        return path
    except Exception as e:
        return f"Error: {str(e)}"


def batch_modify_audio(videos: list[str], audios: list[str], opt: str = "replace") -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        audios = [regularize_path(p) for p in audios]
        if opt == "replace":
            paths = files_audio_replace(videos, audios)
        else:
            paths = files_audio_combine(videos, audios)
        return paths
    except Exception as e:
        return f"Error: {str(e)}"


def batch_compress(videos: list[str], bitrate: int = 8000) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        return files_compress_videos(videos, bitrate)
    except Exception as e:
        return f"Error: {str(e)}"


def batch_extract_audio(videos: list[str]) -> str:
    try:
        videos = [regularize_path(p) for p in videos]
        return files_audio_extract(videos)
    except Exception as e:
        return f"Error: {str(e)}"


# endregion

def apply_option() -> str:
    return f"Save {datetime.datetime.now()}"


def get_file(default_path: str) -> str:
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_path = filedialog.askopenfile()

    root.destroy()
    if file_path is None:
        return default_path
    return file_path.name


def get_files(default_path: list[str]) -> str:
    # FIXME: incorrect function
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_paths = filedialog.askopenfiles()

    root.destroy()
    if file_paths is None:
        return default_path
    return file_paths.name


def get_dir(default_path: str) -> str:
    root = tkinter.Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    dir_path = filedialog.askdirectory()
    root.destroy()
    if dir_path is None:
        return default_path
    return dir_path


# region Gradio Manager

class GradioManager:
    def __init__(self):
        with gr.Blocks(title="Media Processing Tool", head=js) as self.interface:
            gr.Markdown("# Video & Audio Processing Tool")

            with gr.Tab("Single Video"):
                with gr.Tab("Cut Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_input = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                btn_chose_video_to_cut = gr.Button("📂", scale=1)
                            start_time = gr.Textbox(label="Start Time (HH:MM:SS)")
                            end_time = gr.Textbox(label="End Time (HH:MM:SS)")
                            cut_video_btn = gr.Button("Cut Video")
                        with gr.Column():
                            cut_output = gr.Textbox(label="Result", interactive=False)
                            cut_video_output = gr.Video()

                    btn_chose_video_to_cut.click(get_file, inputs=video_input, outputs=video_input)
                    cut_video_btn.click(cut_video, inputs=[video_input, start_time, end_time],
                                        outputs=[cut_output, cut_video_output])

                with gr.Tab("Convert Video to MP3"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_mp4_input = gr.Textbox(label="Video Path", scale=8)
                                btn_chose_mp4_video = gr.Button("📂", scale=1)
                            convert_mp4_btn = gr.Button("Convert to MP3")
                        with gr.Column():
                            convert_mp4_output = gr.Textbox(label="Result", interactive=False)
                            convert_audio_output = gr.Audio()

                    btn_chose_mp4_video.click(get_file, inputs=video_mp4_input, outputs=video_mp4_input)
                    convert_mp4_btn.click(convert_video_to_mp3, inputs=video_mp4_input,
                                          outputs=[convert_mp4_output, convert_audio_output])

                with gr.Tab("Convert Video to Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_to_convert = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                btn_chose_video_to_convert = gr.Button("📂", scale=1)
                                chose_ext = gr.Dropdown(label="Select an extension",
                                                        choices=["mp4", "mov", "avi", "webm", "mkv"])
                            conv_btn = gr.Button("Convert")
                        with gr.Column():
                            conv_output = gr.Textbox(label="Result", interactive=False)

                    btn_chose_video_to_convert.click(get_file, inputs=video_to_convert, outputs=video_to_convert)
                    conv_btn.click(convert_video_to_video, inputs=[video_to_convert, chose_ext], outputs=conv_output)

                with gr.Tab("Modify Audio in Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_path_input = gr.Textbox(label="Video Path", scale=8)
                                btn_cv = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                audio_path_input = gr.Textbox(label="Audio Path", scale=8)
                                btn_ca = gr.Button("📂", scale=1)
                            chose_opt = gr.Dropdown(label="Select a mod", choices=["replace", "combine"])
                            replace_audio_btn = gr.Button("Modify Audio")
                        with gr.Column():
                            replace_text_output = gr.Textbox(label="Result", interactive=False)
                            replace_video_output = gr.Video()

                    btn_cv.click(get_file, inputs=video_path_input, outputs=video_path_input)
                    btn_ca.click(get_file, inputs=audio_path_input, outputs=audio_path_input)
                    replace_audio_btn.click(modify_audio, inputs=[video_path_input, audio_path_input, chose_opt],
                                            outputs=[replace_text_output, replace_video_output])

                with gr.Tab("Compress Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                v_path = gr.Textbox(label="Video Path", scale=8)
                                btn_get_v = gr.Button("📂", scale=1)
                            bitrate = gr.Textbox(label="Target bitrate", value="8000")
                            btn_compress = gr.Button("Compress")
                        with gr.Column():
                            compress_output = gr.Textbox(label="Result", interactive=False)

                    btn_get_v.click(get_file, v_path, v_path)
                    btn_compress.click(compress_vid, [v_path, bitrate], compress_output)

            with gr.Tab("Directory"):
                with gr.Tab("Extract Audio from Directory"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                dir_input = gr.Textbox(label="Directory Path", scale=8)
                                btn_ask_dir = gr.Button("📂", scale=1)
                            extract_btn = gr.Button("Extract Audio")
                        with gr.Column():
                            extract_output = gr.Textbox(label="Result")

                    btn_ask_dir.click(get_dir, inputs=dir_input, outputs=dir_input)
                    extract_btn.click(directory_extract_audio, inputs=dir_input, outputs=extract_output)

                with gr.Tab("Modify audio"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_dir_input = gr.Textbox(label="Video Directory Path", scale=8)
                                btn_video_dir_input = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                audio_dir_input = gr.Textbox(label="Audio Directory Path", scale=8)
                                btn_audio_dir_input = gr.Button("📂", scale=1)
                            dir_chose_opt = gr.Dropdown(label="Select a mod", choices=["replace", "combine"])
                            batch_replace_audio_btn = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            batch_replace_audio_output = gr.Textbox(label="Result")

                    btn_video_dir_input.click(get_dir, inputs=video_dir_input, outputs=video_dir_input)
                    btn_audio_dir_input.click(get_dir, inputs=audio_dir_input, outputs=audio_dir_input)
                    batch_replace_audio_btn.click(directory_audio_modify,
                                                  inputs=[video_dir_input, audio_dir_input, dir_chose_opt],
                                                  outputs=batch_replace_audio_output)

                with gr.Tab("Compress to"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_dir_compress = gr.Textbox(label="Video Directory Path", scale=8)
                                btn_video_dir_input = gr.Button("📂", scale=1)
                            aim_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            btn_batch_compress = gr.Button("Batch compress video")
                        with gr.Column():
                            batch_compress_result = gr.Textbox(label="Result")

                    btn_video_dir_input.click(get_dir, video_dir_compress, video_dir_compress)
                    btn_batch_compress.click(directory_compress, [video_dir_compress, aim_bitrate],
                                             batch_compress_result)

            with gr.Tab("Multiples Videos"):
                gr.Markdown("TODO")
                with gr.Tab("Extract Audios from Videos"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                dir_input = gr.Textbox(label="Directory Path", scale=8)
                                btn_ask_dir = gr.Button("📂", scale=1)
                            extract_btn = gr.Button("Extract Audio")
                        with gr.Column():
                            extract_output = gr.Textbox(label="Result")

                    btn_ask_dir.click(get_dir, inputs=dir_input, outputs=dir_input)
                    extract_btn.click(directory_extract_audio, inputs=dir_input, outputs=extract_output)

                with gr.Tab("Modify audio"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_dir_input = gr.Textbox(label="Video Directory Path", scale=8)
                                btn_video_dir_input = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                audio_dir_input = gr.Textbox(label="Audio Directory Path", scale=8)
                                btn_audio_dir_input = gr.Button("📂", scale=1)
                            dir_chose_opt = gr.Dropdown(label="Select a mod", choices=["replace", "combine"])
                            batch_replace_audio_btn = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            batch_replace_audio_output = gr.Textbox(label="Result")

                    btn_video_dir_input.click(get_dir, inputs=video_dir_input, outputs=video_dir_input)
                    btn_audio_dir_input.click(get_dir, inputs=audio_dir_input, outputs=audio_dir_input)
                    batch_replace_audio_btn.click(directory_audio_modify,
                                                  inputs=[video_dir_input, audio_dir_input, dir_chose_opt],
                                                  outputs=batch_replace_audio_output)

                with gr.Tab("Compress to"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_dir_compress = gr.Textbox(label="Video Directory Path", scale=8)
                                btn_video_dir_input = gr.Button("📂", scale=1)
                            aim_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            btn_batch_compress = gr.Button("Batch compress video")
                        with gr.Column():
                            batch_compress_result = gr.Textbox(label="Result")

                    btn_video_dir_input.click(get_dir, video_dir_compress, video_dir_compress)
                    btn_batch_compress.click(directory_compress, [video_dir_compress, aim_bitrate],
                                             batch_compress_result)

            with gr.Tab("Options"):
                save_btn = gr.Button("Save options")
                save_output = gr.Textbox(label="")

                save_btn.click(apply_option, inputs=[], outputs=save_output)

    def launch(self):
        self.interface.launch(inbrowser=True)


# endregion

if "__main__" == __name__:
    gr_man = GradioManager()
    gr_man.launch()

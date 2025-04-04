import gradio as gr
import datetime
import signal
import sys

from toolbox.Parameters import Params
from script_js import js
from api_gradio.single_file import *
from api_gradio.multiple_files import *
from api_gradio.directory import *
from toolbox.tkinter_getters import *


def on_close(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, on_close)
signal.signal(signal.SIGTERM, on_close)

save_path = "save.json"

Params().load_params_from_json(save_path)


def apply_option(max_workers: int) -> str:
    Params.save_params_to_json({"max_workers": max_workers}, save_path)
    return f"Save {datetime.datetime.now()}"


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
                            start_time = gr.Textbox(label="Start Time (HH:MM:SS or seconds)")
                            end_time = gr.Textbox(label="End Time (HH:MM:SS) or seconds")
                            cut_video_btn = gr.Button("Cut Video")
                        with gr.Column():
                            cut_output = gr.Textbox(label="Result", interactive=False)
                            cut_video_output = gr.Video(sources=["upload"])

                    btn_chose_video_to_cut.click(get_file, inputs=video_input, outputs=video_input)
                    cut_video_btn.click(cut_video, inputs=[video_input, start_time, end_time],
                                        outputs=[cut_output, cut_video_output])

                with gr.Tab("Convert Media"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_to_convert = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                btn_chose_video_to_convert = gr.Button("📂", scale=1)
                                chose_ext = gr.Dropdown(label="Select an extension",
                                                        choices=["mp4", "mov", "avi", "webm", "mkv", "mp3", "wav", "ogg", "flac"])
                            conv_btn = gr.Button("Convert")
                        with gr.Column():
                            convert_output_text = gr.Textbox(label="Result", interactive=False)
                            convert_output_audio = gr.Audio()
                            convert_output_video = gr.Video(sources=["upload"])

                    btn_chose_video_to_convert.click(get_file, inputs=video_to_convert, outputs=video_to_convert)
                    conv_btn.click(convert_media_to_media, inputs=[video_to_convert, chose_ext], outputs=[convert_output_text, convert_output_video, convert_output_audio])

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
                            replace_video_output = gr.Video(sources=['upload'])

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
                with gr.Row():
                    with gr.Column():
                        max_workers = gr.Textbox(label="Max workers:", value="5")
                    with gr.Column():
                        save_btn = gr.Button("Save options")
                        save_output = gr.Textbox(label="")

                save_btn.click(apply_option, inputs=[max_workers], outputs=save_output)

    def launch(self):
        self.interface.launch(inbrowser=True)


# endregion

if "__main__" == __name__:
    gr_man = GradioManager()
    gr_man.launch()

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
                                s_cut_v_path = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                s_cut_get_v_path = gr.Button("📂", scale=1)
                            s_cut_start_time = gr.Textbox(label="Start Time (HH:MM:SS or seconds)")
                            s_cut_end_time = gr.Textbox(label="End Time (HH:MM:SS) or seconds")
                            s_cut_chose_trim_mode = gr.Radio(
                                choices=[
                                    "Frame-accurate trimming: slower but precise",
                                    "Fast seeking: quick but less precise trimming"
                                ],
                                value="Frame-accurate trimming: slower but precise",
                                label="Trimming Mode",
                                type='index'
                            )

                            s_cut_run = gr.Button("Cut Video")
                        with gr.Column():
                            s_cut_text_output = gr.Textbox(label="Result", interactive=False)
                            s_cut_video_output = gr.Video(sources=["upload"])

                    s_cut_get_v_path.click(get_file, inputs=s_cut_v_path, outputs=s_cut_v_path)
                    s_cut_run.click(cut_video,
                                    inputs=[s_cut_v_path, s_cut_start_time, s_cut_end_time, s_cut_chose_trim_mode],
                                    outputs=[s_cut_text_output, s_cut_video_output])

                with gr.Tab("Convert Media"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                s_conv_v_path = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                s_conv_get_v_path = gr.Button("📂", scale=1)
                                s_conv_chose_ext = gr.Dropdown(label="Select an extension",
                                                               choices=["mp4", "mov", "avi", "webm", "mkv", "mp3",
                                                                        "wav",
                                                                        "ogg", "flac"])
                            s_conv_run = gr.Button("Convert")
                        with gr.Column():
                            s_conv_text_output = gr.Textbox(label="Result", interactive=False)
                            s_conv_a_output = gr.Audio()
                            s_conv_v_output = gr.Video(sources=["upload"])

                    s_conv_get_v_path.click(get_file, inputs=s_conv_v_path, outputs=s_conv_v_path)
                    s_conv_run.click(convert_media_to_media, inputs=[s_conv_v_path, s_conv_chose_ext],
                                     outputs=[s_conv_text_output, s_conv_v_output, s_conv_a_output])

                with gr.Tab("Modify Audio in Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                s_modif_video_path = gr.Textbox(label="Video Path", scale=8)
                                s_modif_btn_get_video_path = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                s_modif_audio_path = gr.Textbox(label="Audio Path", scale=8)
                                s_modif_btn_get_audio_path = gr.Button("📂", scale=1)
                            s_modif_chose_opt = gr.Dropdown(label="Select a mode", choices=["replace", "combine"])
                            s_modif_btn_run = gr.Button("Modify Audio")
                        with gr.Column():
                            s_modif_text_output = gr.Textbox(label="Result", interactive=False)
                            s_modif_video_output = gr.Video(sources=['upload'])

                    s_modif_btn_get_video_path.click(get_file, inputs=s_modif_video_path, outputs=s_modif_video_path)
                    s_modif_btn_get_audio_path.click(get_file, inputs=s_modif_audio_path, outputs=s_modif_audio_path)
                    s_modif_btn_run.click(modify_audio,
                                          inputs=[s_modif_video_path, s_modif_audio_path, s_modif_chose_opt],
                                          outputs=[s_modif_text_output, s_modif_video_output])

                with gr.Tab("Compress Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                s_compr_v_path = gr.Textbox(label="Video Path", scale=8)
                                s_compr_btn_get_v_path = gr.Button("📂", scale=1)
                            s_compr_bitrate = gr.Textbox(label="Target bitrate", value="8000")
                            s_compr_min_res = gr.Textbox(label="Minimum resolution", value="1080")
                            s_compr_vcodec = gr.Dropdown(label="Video codec", choices=["hevc_nvenc", "libx264", "libvpx-vp9", "h264_nvenc"])
                            s_compr_run = gr.Button("Compress")
                        with gr.Column():
                            s_cv_output = gr.Textbox(label="Result", interactive=False)

                    s_compr_btn_get_v_path.click(get_file, s_compr_v_path, s_compr_v_path)
                    s_compr_run.click(compress_vid, [s_compr_v_path, s_compr_bitrate, s_compr_min_res, s_compr_vcodec],
                                      s_cv_output)

            with gr.Tab("Directory"):
                with gr.Tab("Extract Audio from Directory"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_extr_v_path = gr.Textbox(label="Directory Path", scale=8)
                                d_extr_btn_get_v_path = gr.Button("📂", scale=1)
                            d_extr_run = gr.Button("Extract Audio")
                        with gr.Column():
                            d_extr_output = gr.Textbox(label="Result")

                    d_extr_btn_get_v_path.click(get_dir, inputs=d_extr_v_path, outputs=d_extr_v_path)
                    d_extr_run.click(directory_extract_audio, inputs=d_extr_v_path, outputs=d_extr_output)

                with gr.Tab("Modify audio"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_modif_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                d_modif_btn_get_v_path = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                d_modif_a_path = gr.Textbox(label="Audio Directory Path", scale=8)
                                d_modif_btn_get_a_path = gr.Button("📂", scale=1)
                            d_modif_mode_opt = gr.Dropdown(label="Select a mode", choices=["replace", "combine"])
                            d_modif_run = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            d_modif_output = gr.Textbox(label="Result")

                    d_modif_btn_get_v_path.click(get_dir, inputs=d_modif_v_path, outputs=d_modif_v_path)
                    d_modif_btn_get_a_path.click(get_dir, inputs=d_modif_a_path, outputs=d_modif_a_path)
                    d_modif_run.click(directory_audio_modify,
                                      inputs=[d_modif_v_path, d_modif_a_path, d_modif_mode_opt],
                                      outputs=d_modif_output)

                with gr.Tab("Compress to"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_compr_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                d_compr_btn_get_v_path = gr.Button("📂", scale=1)
                            d_compr_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            d_compr_run = gr.Button("Batch compress video")
                        with gr.Column():
                            d_compr_output = gr.Textbox(label="Result")

                    d_compr_btn_get_v_path.click(get_dir, d_compr_v_path, d_compr_v_path)
                    d_compr_run.click(directory_compress, [d_compr_v_path, d_compr_bitrate],
                                      d_compr_output)

            with gr.Tab("Multiples Videos"):
                gr.Markdown("TODO")
                with gr.Tab("Extract Audios from Videos"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_extr_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                m_extr_btn_get_v_path = gr.Button("📂", scale=1)
                            m_extr_run = gr.Button("Extract Audio")
                        with gr.Column():
                            m_extr_output = gr.Textbox(label="Result")

                    m_extr_btn_get_v_path.click(get_dir, inputs=m_extr_v_path, outputs=m_extr_v_path)
                    m_extr_run.click(directory_extract_audio, inputs=m_extr_v_path, outputs=m_extr_output)

                with gr.Tab("Modify audio"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_modif_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                m_modif_btn_get_v_path = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                m_modif_a_path = gr.Textbox(label="Audio Directory Path", scale=8)
                                m_modif_btn_get_a_path = gr.Button("📂", scale=1)
                            m_modif_opt_mode = gr.Dropdown(label="Select a mode", choices=["replace", "combine"])
                            m_modif_run = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            m_modif_output = gr.Textbox(label="Result")

                    m_modif_btn_get_v_path.click(get_dir, inputs=m_modif_v_path, outputs=m_modif_v_path)
                    m_modif_btn_get_a_path.click(get_dir, inputs=m_modif_a_path, outputs=m_modif_a_path)
                    m_modif_run.click(directory_audio_modify,
                                      inputs=[m_modif_v_path, m_modif_a_path, m_modif_opt_mode],
                                      outputs=m_modif_output)

                with gr.Tab("Compress to"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_compr_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                m_compr_get_v_path = gr.Button("📂", scale=1)
                            m_compr_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            m_compr_run = gr.Button("Batch compress video")
                        with gr.Column():
                            m_compr_output = gr.Textbox(label="Result")

                    m_compr_get_v_path.click(get_dir, m_compr_v_path, m_compr_v_path)
                    m_compr_run.click(directory_compress, [m_compr_v_path, m_compr_bitrate],
                                      m_compr_output)

            with gr.Tab("Options"):
                with gr.Row():
                    with gr.Column():
                        opt_max_workers = gr.Textbox(label="Max workers:", value="5")
                    with gr.Column():
                        opt_btn_save = gr.Button("Save options")
                        opt_output = gr.Textbox(label="")

                opt_btn_save.click(apply_option, inputs=[opt_max_workers], outputs=opt_output)

    def launch(self):
        self.interface.launch(inbrowser=True)


# endregion

if "__main__" == __name__:
    gr_man = GradioManager()
    gr_man.launch()

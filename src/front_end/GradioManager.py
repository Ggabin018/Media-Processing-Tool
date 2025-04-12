import datetime
import signal
import sys

import gradio as gr

from middle_end.directory import *
from middle_end.single_file import *
from middle_end.multiple_files import *
from front_end.script_js import js
from toolbox.Parameters import Params
from toolbox.tkinter_getters import *


def on_close(sig, frame):
    sys.exit(0)


signal.signal(signal.SIGINT, on_close)
signal.signal(signal.SIGTERM, on_close)

save_path = "save.json"

params = Params()
params.load_params_from_json(save_path)


def apply_option(max_workers: int, vcodec) -> str:
    Params.save_params_to_json({"max_workers": max_workers, "vcodec": vcodec}, save_path)
    params.load_params_from_json(save_path)
    return f"Save {datetime.datetime.now()}"


# region Gradio Manager

def ui_reload():
    return (
        params.get_max_workers(),   # opt_max_workers
        params.get_vcodec(),        # opt_vcodec
        params.get_vcodec(),        # s_compr_vcodec
        params.get_vcodec(),        # d_compr_vcodec
        params.get_vcodec()         # m_compr_vcodec
    )


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
                            s_compr_vcodec = gr.Dropdown(label="Video codec", value=params.get_vcodec(),
                                                         choices=["hevc_nvenc", "libx264", "libvpx-vp9", "h264_nvenc"])
                            s_compr_run = gr.Button("Compress")
                        with gr.Column():
                            s_cv_output = gr.Textbox(label="Result", interactive=False)

                    s_compr_btn_get_v_path.click(get_file, s_compr_v_path, s_compr_v_path)
                    s_compr_run.click(compress_vid, [s_compr_v_path, s_compr_bitrate, s_compr_min_res, s_compr_vcodec],
                                      s_cv_output)

            with gr.Tab("Directory"):
                with gr.Tab("Convert medias"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_conv_v_path = gr.Textbox(label="Directory Path", scale=8)
                                d_conv_btn_get_v_path = gr.Button("📂", scale=1)
                                d_conv_chose_ext = gr.Dropdown(label="Select an extension",
                                                               choices=["mp4", "mov", "avi", "webm", "mkv", "mp3",
                                                                        "wav",
                                                                        "ogg", "flac"])
                            d_conv_run = gr.Button("Convert")
                        with gr.Column():
                            d_conv_output = gr.Textbox(label="Result", interactive=False)

                    d_conv_btn_get_v_path.click(get_dir, inputs=d_conv_v_path, outputs=d_conv_v_path)
                    d_conv_run.click(directory_media2media, inputs=[d_conv_v_path, d_conv_chose_ext],
                                     outputs=d_conv_output)

                with gr.Tab("Modify audio"):
                    gr.Markdown("Random choice mapping between videos and audios")
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_modif_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                d_modif_btn_get_v_path = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                d_modif_a_path = gr.Textbox(label="Audio Directory Path", scale=8)
                                d_modif_btn_get_a_path = gr.Button("📂", scale=1)
                            d_modif_mode_opt = gr.Dropdown(label="Select a mode", choices=["replace", "combine"])
                            d_modif_randomize = gr.Checkbox(label="Random order", value=True)
                            d_modif_run = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            d_modif_output = gr.Textbox(label="Result", interactive=False)

                    d_modif_btn_get_v_path.click(get_dir, inputs=d_modif_v_path, outputs=d_modif_v_path)
                    d_modif_btn_get_a_path.click(get_dir, inputs=d_modif_a_path, outputs=d_modif_a_path)
                    d_modif_run.click(directory_audio_modify,
                                      inputs=[d_modif_v_path, d_modif_a_path, d_modif_mode_opt, d_modif_randomize],
                                      outputs=d_modif_output)

                with gr.Tab("Compress Videos"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                d_compr_v_path = gr.Textbox(label="Video Directory Path", scale=8)
                                d_compr_btn_get_v_path = gr.Button("📂", scale=1)
                            d_compr_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            d_compr_min_res = gr.Textbox(label="Minimum resolution", value="1080")
                            d_compr_vcodec = gr.Dropdown(label="Video codec", value=params.get_vcodec(),
                                                         choices=["hevc_nvenc", "libx264", "libvpx-vp9", "h264_nvenc"])

                            d_compr_run = gr.Button("Batch compress video")
                        with gr.Column():
                            d_compr_output = gr.Textbox(label="Result", interactive=False)

                    d_compr_btn_get_v_path.click(get_dir, d_compr_v_path, d_compr_v_path)
                    d_compr_run.click(directory_compress,
                                      [d_compr_v_path, d_compr_bitrate, d_compr_min_res, d_compr_vcodec],
                                      d_compr_output)

            with gr.Tab("Multiples Videos"):
                with gr.Tab("Convert Videos"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_cvv_v_path = gr.Dataframe(
                                    headers=["Video Paths"],
                                    datatype="str",
                                    col_count=(1, "fixed"),
                                    interactive=True,
                                    row_count=1,
                                    type="array",
                                    wrap=True,
                                    scale=8
                                )
                                m_cvv_btn_get_v_path = gr.Button("📂")
                                m_cvv_chose_ext = gr.Dropdown(label="Select an extension",
                                                              choices=["mp4", "mov", "avi", "webm", "mkv"])
                            m_cvv_run = gr.Button("Convert")
                        with gr.Column():
                            m_cvv_output = gr.Textbox(label="Result")

                    m_cvv_btn_get_v_path.click(get_video_files, inputs=m_cvv_v_path, outputs=m_cvv_v_path)
                    m_cvv_run.click(batch_convert, inputs=[m_cvv_v_path, m_cvv_chose_ext], outputs=m_cvv_output)

                with gr.Tab("Convert Audios"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_cva_a_path = gr.Dataframe(
                                    headers=["Audio Paths"],
                                    datatype="str",
                                    col_count=(1, "fixed"),
                                    interactive=True,
                                    row_count=1,
                                    type="array",
                                    wrap=True,
                                    scale=8
                                )
                                m_cva_btn_get_a_path = gr.Button("📂")
                                m_cva_chose_ext = gr.Dropdown(label="Select an extension",
                                                               choices=["mp3","wav","ogg", "flac"])
                            m_cva_run = gr.Button("Convert")
                        with gr.Column():
                            m_cva_output = gr.Textbox(label="Result")

                m_cva_btn_get_a_path.click(get_audio_files, inputs=m_cva_a_path, outputs=m_cva_a_path)
                m_cva_run.click(batch_convert, inputs=[m_cva_a_path, m_cva_chose_ext], outputs=m_cva_output)

                with gr.Tab("Modify audio"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_modif_v_path = gr.Dataframe(
                                    headers=["Video Paths"],
                                    datatype="str",
                                    col_count=(1, "fixed"),
                                    interactive=True,
                                    row_count=1,
                                    type="array",
                                    wrap=True,
                                    scale=8
                                )
                                m_modif_btn_get_v_path = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                m_modif_a_path = gr.Dataframe(
                                    headers=["Audio Paths"],
                                    datatype="str",
                                    col_count=(1, "fixed"),
                                    interactive=True,
                                    row_count=1,
                                    type="array",
                                    wrap=True,
                                    scale=8
                                )
                                m_modif_btn_get_a_path = gr.Button("📂", scale=1)
                            m_modif_opt_mode = gr.Dropdown(label="Select a mode", choices=["replace", "combine"])
                            m_modif_randomize = gr.Checkbox(label="Random order", value=True)
                            m_modif_run = gr.Button("Batch Modify Audio")
                        with gr.Column():
                            m_modif_output = gr.Textbox(label="Result")

                m_modif_btn_get_v_path.click(get_video_files, inputs=m_modif_v_path, outputs=m_modif_v_path)
                m_modif_btn_get_a_path.click(get_audio_files, inputs=m_modif_a_path, outputs=m_modif_a_path)
                m_modif_run.click(batch_modify_audio,
                                  inputs=[m_modif_v_path, m_modif_a_path, m_modif_opt_mode, m_modif_randomize],
                                  outputs=m_modif_output)

                with gr.Tab("Compress to"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                m_compr_v_path = gr.Dataframe(
                                    headers=["Video Paths"],
                                    datatype="str",
                                    col_count=(1, "fixed"),
                                    interactive=True,
                                    row_count=1,
                                    type="array",
                                    wrap=True,
                                    scale=8
                                )
                                m_compr_get_v_path = gr.Button("📂", scale=1)
                            m_compr_bitrate = gr.Textbox(label="Bitrate wanted:", value="8000")
                            m_compr_min_res = gr.Textbox(label="Minimum resolution", value="1080")
                            m_compr_vcodec = gr.Dropdown(label="Video codec", value=params.get_vcodec(),
                                                         choices=["hevc_nvenc", "libx264", "libvpx-vp9", "h264_nvenc"])
                            
                            m_compr_run = gr.Button("Batch compress video")
                        with gr.Column():
                            m_compr_output = gr.Textbox(label="Result")

                m_compr_get_v_path.click(get_video_files, m_compr_v_path, m_compr_v_path)
                m_compr_run.click(batch_compress, [m_compr_v_path, m_compr_bitrate, m_compr_min_res, m_compr_vcodec],
                                  m_compr_output)

            with gr.Tab("Options"):
                with gr.Row():
                    with gr.Column():
                        opt_max_workers = gr.Textbox(label="Max workers:", value=str(params.get_max_workers()))
                        opt_vcodec = gr.Dropdown(label="Default video codec:", value=params.get_vcodec(),
                                                 choices=["hevc_nvenc", "libx264", "libvpx-vp9", "h264_nvenc"])
                    with gr.Column():
                        with gr.Row():
                            opt_btn_save = gr.Button("Save options")
                            opt_btn_reload_ui = gr.Button("Reload UI")
                        opt_output = gr.Textbox(label="")

                opt_btn_save.click(apply_option, inputs=[opt_max_workers, opt_vcodec], outputs=opt_output)
                opt_btn_reload_ui.click(ui_reload, outputs=[
                    opt_max_workers,
                    opt_vcodec,
                    s_compr_vcodec,
                    d_compr_vcodec,
                    m_compr_vcodec
                ])

    def launch(self):
        self.interface.launch(inbrowser=True)

# endregion

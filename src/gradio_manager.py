import gradio as gr

from dir_manip import (
    dir_audio_extract,
    dir_audio_replace, 
    dir_audio_combine
)
from convertisseur import convertir_video_to_mp3, conv_video_to_video
from video_modif import video_cut
from audio_modif import audio_replace

import datetime

from shutil import copy
import os
import tempfile

import signal
import sys

import tkinter
from tkinter import filedialog

temp_dir = tempfile.gettempdir()

def reg_path(path:str):
    return path.replace('"', '')

dst_path = None
def clean(sig, frame):
    if dst_path != None:
        os.remove(dst_path)
    sys.exit(0)
signal.signal(signal.SIGINT, clean)
signal.signal(signal.SIGTERM, clean)

# region Gradio functions --------------------------------------------------

def on_change_file(src_path):
    global dst_path
    if dst_path != None and os.path.exists(dst_path):
        os.remove(dst_path)
    dst_path=os.path.join(temp_dir, os.path.basename(src_path))
    return copy(src_path, dst_path)

def cut_video(video_path, start, end):
    try:
        path = video_cut(reg_path(video_path), start=start, end=end)
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}"

def convert_video_to_mp3(video_path):
    try:
        path = convertir_video_to_mp3(reg_path(video_path))
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}"
    
def convert_video_to_video(video_path, ext): # TODO
    try:
        path = conv_video_to_video(reg_path(video_path), ext)
        return path
    except Exception as e:
        return f"Error: {str(e)}"


def replace_audio(video_path, audio_path): # TODO
    try:
        return audio_replace(video_path, audio_path)
    except Exception as e:
        return f"Error: {str(e)}"
    
def extract_audio_from_dir(video_dir_path): #TODO
    try:
        dir_audio_extract(video_dir_path)
        return "Audio extracted from all videos in the directory"
    except Exception as e:
        return f"Error: {str(e)}"
    
def batch_audio_replace(video_dir_path, audio_dir_path): # TODO
    try:
        dir_audio_replace(video_dir_path, audio_dir_path)
        return "Audio replaced in all videos in the directory"
    except Exception as e:
        return f"Error: {str(e)}"

def batch_audio_combine(video_dir_path, audio_dir_path): # TODO
    try:
        dir_audio_combine(video_dir_path, audio_dir_path)
        return "Audios combined successfully in all videos"
    except Exception as e:
        return f"Error: {str(e)}"
    
def apply_option():
    return f"Save {datetime.datetime.now()}"

def get_file(default_path):
    root = tkinter.Tk()
    root.withdraw()

    file_path = filedialog.askopenfile()
    root.destroy()
    if file_path is None:
        return default_path
    return file_path.name

# endregion 


class GradioManager:
    def __init__(self):
        with gr.Blocks(title="Media Processing Tool") as self.interface:
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
                            cut_video_output = gr.Video(autoplay=True)
                    
                    btn_chose_video_to_cut.click(get_file,inputs=video_input, outputs=video_input)
                    cut_video_btn.click(cut_video, inputs=[video_input, start_time, end_time], outputs=[cut_output, cut_video_output])

                with gr.Tab("Convert Video to MP3"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_mp4_input = gr.Textbox(label="Video Path", scale=8)
                                btn_chose_mp4_video = gr.Button("📂", scale=1)
                            convert_mp4_btn = gr.Button("Convert to MP3")
                        with gr.Column():
                            convert_mp4_output = gr.Textbox(label="Result", interactive=False)
                            convert_audio_output = gr.Audio(autoplay=True)
                    
                    btn_chose_mp4_video.click(get_file,inputs=video_mp4_input, outputs=video_mp4_input)
                    convert_mp4_btn.click(convert_video_to_mp3, inputs=video_mp4_input, outputs=[convert_mp4_output, convert_audio_output])
            
                with gr.Tab("Convert Video to Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_to_convert = gr.Textbox(label="Video Path", placeholder="required", scale=8)
                                btn_chose_video_to_convert = gr.Button("📂", scale=1)
                                chose_ext=gr.Dropdown(label="Select an extension", choices=["mp4", "mov", "avi", "webm", "mkv"])
                            conv_btn = gr.Button("Convert")
                        with gr.Column():
                            conv_output = gr.Textbox(label="Result", interactive=False)
                    
                    btn_chose_video_to_convert.click(get_file,inputs=video_to_convert, outputs=video_to_convert)
                    conv_btn.click(convert_video_to_video, inputs=[video_to_convert, chose_ext], outputs=conv_output)
                
                with gr.Tab("Replace Audio in Video"):
                    with gr.Row():
                        with gr.Column():
                            video_path_input = gr.Textbox(label="Video Path")
                            audio_path_input = gr.Textbox(label="Audio Path")
                            replace_audio_btn = gr.Button("Replace Audio")
                        with gr.Column():
                            replace_audio_output = gr.Textbox(label="Result", interactive=False)
                            replace_video_output = gr.Video(autoplay=True)
                    
                    replace_audio_btn.click(replace_audio, inputs=[video_path_input, audio_path_input], outputs=replace_audio_output)
                    replace_audio_output.change(on_change_file, inputs=replace_audio_output, outputs=replace_video_output)
            
            with gr.Tab("Multiples Videos"):
                with gr.Tab("Extract Audio from Directory"):
                    dir_input = gr.Textbox(label="Directory Path")
                    extract_btn = gr.Button("Extract Audio")
                    extract_output = gr.Textbox(label="Result")
                    
                    extract_btn.click(extract_audio_from_dir, inputs=dir_input, outputs=extract_output)
                
                with gr.Tab("Batch Replace Audio"):
                    video_dir_input = gr.Textbox(label="Video Directory Path")
                    audio_dir_input = gr.Textbox(label="Audio Directory Path")
                    batch_replace_audio_btn = gr.Button("Batch Replace Audio")
                    batch_replace_audio_output = gr.Textbox(label="Result")
                    
                    batch_replace_audio_btn.click(batch_audio_replace, inputs=[video_dir_input, audio_dir_input], outputs=batch_replace_audio_output)
                
                with gr.Tab("Batch Combine Audio"):
                    combine_video_dir_input = gr.Textbox(label="Video Directory Path")
                    combine_audio_dir_input = gr.Textbox(label="Audio Directory Path")
                    batch_combine_audio_btn = gr.Button("Batch Combine Audio")
                    batch_combine_audio_output = gr.Textbox(label="Result")
                    
                    batch_combine_audio_btn.click(batch_audio_combine, inputs=[combine_video_dir_input, combine_audio_dir_input], outputs=batch_combine_audio_output)

            with gr.Tab("Options"):
                save_btn = gr.Button("Save options")
                save_output = gr.Textbox(label="")

                save_btn.click(apply_option, inputs=[], outputs=save_output)

    def launch(self):
        self.interface.launch(inbrowser=True)

if "__main__" == __name__:
    gr_man = GradioManager()
    gr_man.launch()
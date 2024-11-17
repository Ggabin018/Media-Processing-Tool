import gradio as gr

from dir_manip import (
    dir_audio_extract,
    dir_audio_replace, 
    dir_audio_combine,
    dir_convert_video_to_video
)
from convertisseur import convertir_video_to_mp3, conv_video_to_video
from video_modif import video_cut
from audio_modif import audio_replace, audio_combine

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

from DraggableListbox import WindowDragListBox

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

# region Single File functions

def on_change_file(src_path):
    global dst_path
    if dst_path != None and os.path.exists(dst_path):
        os.remove(dst_path)
    dst_path=os.path.join(temp_dir, os.path.basename(src_path))
    return copy(src_path, dst_path)

def cut_video(video_path, start, end):
    try:
        video_path = reg_path(video_path)
        if not os.path.exists(video_path):
            raise Exception(f"{path} does not exit")
        
        path = video_cut(video_path, start=start, end=end)
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}", None

def convert_video_to_mp3(video_path):
    try:
        path = convertir_video_to_mp3(reg_path(video_path))
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}", None
    
def convert_video_to_video(video_path, ext):
    try:
        path = conv_video_to_video(reg_path(video_path), ext)
        return path
    except Exception as e:
        return f"Error: {str(e)}", None

def modify_audio(video_path, audio_path, opt="replace"): # TODO
    try:
        if opt == "replace":
            path = audio_replace(reg_path(video_path), reg_path(audio_path))
        else:
            path = audio_combine(reg_path(video_path), reg_path(audio_path))
        return path, on_change_file(path)
    except Exception as e:
        return f"Error: {str(e)}", None
    
#endregion

# region Multiples Files functions

def extract_audio_from_dir(video_dir_path):
    try:
        return dir_audio_extract(reg_path(video_dir_path))
    except Exception as e:
        return f"Error: {str(e)}", None
    
def batch_audio_modifier(video_dir_path, audio_dir_path, opt="replace"):
    try:
        if opt == "replace":
            return dir_audio_replace(video_dir_path, audio_dir_path)
        return dir_audio_combine(video_dir_path, audio_dir_path)
    except Exception as e:
        return f"Error: {str(e)}", None

# endregion 

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

def get_dir(default_path):
    root = tkinter.Tk()
    root.withdraw()

    dir_path = filedialog.askdirectory()
    root.destroy()
    if dir_path is None:
        return default_path
    return dir_path

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
                
                with gr.Tab("Modify Audio in Video"):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row(equal_height=True):
                                video_path_input = gr.Textbox(label="Video Path", scale=8)
                                btn_cv = gr.Button("📂", scale=1)
                            with gr.Row(equal_height=True):
                                audio_path_input = gr.Textbox(label="Audio Path", scale=8)
                                btn_ca = gr.Button("📂", scale=1)
                            chose_opt=gr.Dropdown(label="Select a mod", choices=["replace", "combine"])
                            replace_audio_btn = gr.Button("Modify Audio")
                        with gr.Column():
                            replace_text_output = gr.Textbox(label="Result", interactive=False)
                            replace_video_output = gr.Video(autoplay=True)
                    
                    btn_cv.click(get_file,inputs=video_path_input, outputs=video_path_input)
                    btn_ca.click(get_file,inputs=audio_path_input, outputs=audio_path_input)
                    replace_audio_btn.click(modify_audio, inputs=[video_path_input, audio_path_input, chose_opt], outputs=[replace_text_output, replace_video_output])
            
            with gr.Tab("Directory"):
                with gr.Tab("Extract Audio from Directory"):
                    with gr.Row(equal_height=True):
                        dir_input = gr.Textbox(label="Directory Path", scale=8)
                        btn_ask_dir = gr.Button("📂", scale=1)
                    extract_btn = gr.Button("Extract Audio")
                    extract_output = gr.Textbox(label="Result")
                    
                    btn_ask_dir.click(get_dir,inputs=dir_input, outputs=dir_input)
                    extract_btn.click(extract_audio_from_dir, inputs=dir_input, outputs=extract_output)
                
                with gr.Tab("Modify audio"):
                    with gr.Row(equal_height=True):
                        video_dir_input = gr.Textbox(label="Video Directory Path", scale=8)
                        btn_video_dir_input= gr.Button("📂", scale=1)
                    with gr.Row(equal_height=True):
                        audio_dir_input = gr.Textbox(label="Audio Directory Path", scale=8)
                        btn_audio_dir_input= gr.Button("📂", scale=1)
                    dir_chose_opt=gr.Dropdown(label="Select a mod", choices=["replace", "combine"])
                    batch_replace_audio_btn = gr.Button("Batch Modify Audio")
                    batch_replace_audio_output = gr.Textbox(label="Result")
                    
                    btn_video_dir_input.click(get_dir,inputs=video_dir_input, outputs=video_dir_input)
                    btn_audio_dir_input.click(get_dir,inputs=audio_dir_input, outputs=audio_dir_input)
                    batch_replace_audio_btn.click(batch_audio_modifier, inputs=[video_dir_input, audio_dir_input, dir_chose_opt], outputs=batch_replace_audio_output)

            with gr.Tab("Multiples Videos"):
                with gr.Tab("Convert Video to MP3"):
                    gr.Markdown("# TODO")
                with gr.Tab("Convert Video to Video"):
                    gr.Markdown("# TODO")
                with gr.Tab("Modify Audio in Video"):
                    gr.Markdown("# TODO")
            
            with gr.Tab("Options"):
                save_btn = gr.Button("Save options")
                save_output = gr.Textbox(label="")

                save_btn.click(apply_option, inputs=[], outputs=save_output)


    def launch(self):
        self.interface.launch(inbrowser=True)

if "__main__" == __name__:
    gr_man = GradioManager()
    gr_man.launch()
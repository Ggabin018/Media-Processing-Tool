import os
from thread import exec

def get_video_duration(video_path:str)->float:
    """
    :param video_path: chemin absolu de la vidéo
    :return: durée de la vidéo en secondes
    """
    ffmpeg_command = f'ffprobe -v error -select_streams v:0 -show_entries format=duration -of csv=p=0 "{video_path}"'

    duration_info = os.popen(ffmpeg_command).read().strip()

    return float(duration_info)

def get_resolution(video_path:str)->tuple[int,int]:
    """
    :param video_path: chemin abs vidéo
    :return: width, height
    """
    ffmpeg_command = f'ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "{video_path}"'

    resolution_info = os.popen(ffmpeg_command).read()

    return map(int, resolution_info.split('x'))

def get_video_bitrate(video_path: str) -> float:
    """
    get video bitrate in kbps
    :param video_path: Absolute path to the video file
    :return: Bitrate of the video in kbps
    """
    ffmpeg_command = f'ffprobe -v error -select_streams v:0 -show_entries format=bit_rate -of csv=p=0 "{video_path}"'
    
    bitrate_info = os.popen(ffmpeg_command).read().strip()
    
    return float(bitrate_info) / 1000


def video_cut(input_video:str, start=None, end=None)->str:
    """
    cut a video from start to end
    :param start: format "HH:MM:SS"
    :param end: format "HH:MM:SS"
    """
    start_option = f"-ss {start}" if start is not None and start != "" else ""
    end_option = f"-to {end}" if end is not None and end != "" else ""

    output_video = os.path.splitext(input_video)[0] + "__cut.mp4"
    ffmpeg_command = (
        #f'ffmpeg -y -i "{input_video}" {start_option} {end_option} -c copy "{output_video}"' # fast
        f'ffmpeg -y -hwaccel cuda -i "{input_video}" -c:v hevc_nvenc -b:v {get_video_bitrate(input_video)}k {start_option} {end_option} "{output_video}"'          # slow but no bug
    )

    exec(ffmpeg_command)
    
    return output_video


def video_upscale(input_video:str, factor:int)->str:
    """
    multiply the resolution of a video
    BUG sometimes crash with specific video
    """
    output_video = os.path.splitext(input_video)[0] + f"__up{factor}.mp4"
    ffmpeg_command = (
        f'ffmpeg -i "{input_video}" -vf "scale=iw*{factor}:ih*{factor},unsharp=5:5:1.0:5:5:0.0, hqdn3d=luma_spatial=4:chroma_spatial=4:luma_tmp=4:chroma_tmp=4" -c:a copy "{output_video}"'
    )
    exec(ffmpeg_command)
    return output_video

def video_compress(video_path:str, output_filename:str="", target_bitrate:int=8000):
    """
    convert in 1080p with CUDA while keeping ratio
    :param output_folder: if not precise, add __compressed to filename
    """
    target_bitrate = int(target_bitrate)
    try:
        width, height = get_resolution(video_path)

        if width >= 1080 or height >= 1080:
            if output_filename == "":
                output_filename = os.path.splitext(video_path)[0] + f"__compressed.mp4"

            if width > height:
                ffmpeg_command = (
                    f'ffmpeg -y -hwaccel cuda -i "{video_path}" -c:v hevc_nvenc -b:v {target_bitrate}k -vf "scale=-2:1080" -c:a copy -pix_fmt yuv420p "{output_filename}"'
                )
            else:
                ffmpeg_command = (
                    f'ffmpeg -y -hwaccel cuda -i "{video_path}" -c:v hevc_nvenc -b:v {target_bitrate}k -vf "scale=1080:-2" -c:a copy -pix_fmt yuv420p "{output_filename}"'
                )

            exec(ffmpeg_command)
            
            return output_filename
        else:
            print(f" {video_path} is already <= to 1080p.")
            return video_path
    except Exception as e:
        print(f"Failure with {video_path}. Error : {str(e)}")
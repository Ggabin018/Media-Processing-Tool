import os


def hhmmss_to_seconds(time_str):
    """Convert HH:MM:SS to total seconds."""
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def format_time(seconds: float) -> str:
    """Format seconds as HH:MM:SS.ms."""
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"

def regularize_path(path: str) -> str:
    path = path.strip('\'"')
    path = path.replace('\\', '/')
    path = os.path.normpath(path)
    return path
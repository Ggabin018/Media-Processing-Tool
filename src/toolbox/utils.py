import os


def hhmmss_to_seconds(time_str):
    """Convert HH:MM:SS to total seconds."""
    h, m, s = map(int, time_str.split(":"))
    return h * 3600 + m * 60 + s

def regularize_path(path: str) -> str:
    path = path.strip('\'"')
    path = path.replace('\\', '/')
    path = os.path.normpath(path)
    return path
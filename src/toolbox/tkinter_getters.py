from tkinter import filedialog, Tk
from typing import IO


def get_file(default_path: str) -> str:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_path = filedialog.askopenfile()

    root.destroy()
    if file_path is None:
        return default_path
    return file_path.name


def get_files(default_path: list[str]) -> list[str]:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_paths:tuple[IO, ...] = filedialog.askopenfiles()

    root.destroy()
    if file_paths is None:
        return default_path
    return [io.name for io in file_paths]


def get_dir(default_path: str) -> str:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    dir_path = filedialog.askdirectory()
    root.destroy()
    if dir_path is None:
        return default_path
    return dir_path
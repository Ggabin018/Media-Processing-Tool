from tkinter import filedialog, Tk


def get_file(default_path: str) -> str:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_path = filedialog.askopenfile()

    root.destroy()
    if file_path is None:
        return default_path
    return file_path.name

def get_video_files(default_path: list[list[str]]) -> list[list[str]]:
    return get_files(default_path, [
        ("Video files", "*.mp4 *.avi *.mkv *.mov"),
        ("All files", "*.*")
    ])

def get_audio_files(default_path: list[list[str]]) -> list[list[str]]:
    return get_files(default_path, [
        ("Audio files", "*.mp3 *.wav *.ogg *.flac"),
        ("All files", "*.*")
    ])

def get_files(default_path: list[list[str]], filetypes) -> list[list[str]]:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    file_paths = filedialog.askopenfiles(filetypes=filetypes)

    root.destroy()
    if not file_paths:
        return default_path

    result = default_path.copy() if default_path else []

    new_paths = [io.name for io in file_paths]
    if result:
        for path in new_paths:
            result.append([path])
    else:
        result = [[path] for path in new_paths]

    return result


def get_dir(default_path: str) -> str:
    root = Tk()
    root.withdraw()
    root.wm_attributes('-topmost', 1)

    dir_path = filedialog.askdirectory()
    root.destroy()
    if dir_path is None:
        return default_path
    return dir_path

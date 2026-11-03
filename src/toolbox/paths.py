"""Clean and check paths typed or pasted in the UI."""
import os


def clean_path(raw: str | None) -> str:
    """
    Strip surrounding spaces and quotes (e.g. Windows "Copy as path"), then normalize separators.
    :raise ValueError: if the path is empty
    """
    path = (raw or "").strip().strip('"\'').strip()
    if not path:
        raise ValueError("Empty path")
    return os.path.normpath(path.replace("\\", "/"))


def require_file(raw: str | None) -> str:
    """Clean a path and check it is an existing file."""
    path = clean_path(raw)
    if not os.path.isfile(path):
        raise FileNotFoundError(f"{path} does not exist")
    return path


def require_dir(raw: str | None) -> str:
    """Clean a path and check it is an existing directory."""
    path = clean_path(raw)
    if not os.path.isdir(path):
        raise NotADirectoryError(f"{path} is not a directory")
    return path


def clean_file_list(rows: list | None) -> list[str]:
    """
    Turn the rows of a gr.Dataframe (list of [path]) into a list of existing files.
    Empty cells are skipped.
    :raise FileNotFoundError: listing every missing file
    """
    files, missing = [], []
    for row in rows or []:
        cell = row[0] if isinstance(row, (list, tuple)) and row else row
        if not isinstance(cell, str) or not cell.strip().strip('"\'').strip():
            continue
        path = clean_path(cell)
        if os.path.isfile(path):
            files.append(path)
        else:
            missing.append(path)
    if missing:
        raise FileNotFoundError("Files not found: " + ", ".join(missing))
    return files

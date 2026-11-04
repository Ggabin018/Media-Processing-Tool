class FileTypeError(Exception):
    pass


class ArgumentError(Exception):
    pass


class FfmpegError(Exception):
    """ffmpeg exited with a non-zero code. `stderr_tail` holds its last error lines."""

    def __init__(self, returncode: int, stderr_tail: list[str]):
        if returncode >= 2 ** 31:  # Windows returns NTSTATUS / negative codes as unsigned 32 bits
            returncode -= 2 ** 32
        self.returncode = returncode
        self.stderr_tail = stderr_tail
        last = " | ".join(stderr_tail[-3:]) or "no error output"
        super().__init__(f"ffmpeg exited with code {returncode}: {last}")

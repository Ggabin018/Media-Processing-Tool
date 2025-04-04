import sys

from toolbox.utils import format_time


def progress_bar(duration: float, process):
    progress_buffer = ""
    progress_info = {}
    bar_width = 100

    while process.poll() is None:
        char = process.stdout.read(1).decode('utf-8', errors='replace')
        progress_buffer += char

        if char == '\n':
            line = progress_buffer.strip()
            progress_buffer = ""

            if '=' in line:
                key, value = line.split('=', 1)
                progress_info[key.strip()] = value.strip()

            # Update progress bar on 'progress=continue' or 'progress=end'
            if line in ('progress=continue', 'progress=end'):
                out_time = progress_info.get('out_time', '00:00:00.000000').split('.')[0]
                fps = progress_info.get('fps', '0')
                speed = progress_info.get('speed', '0x')

                # Calculate progress percentage
                h, m, s = map(float, out_time.split(':'))
                current_seconds = h * 3600 + m * 60 + s
                percentage = min(100, int(current_seconds / duration * 100))

                # Build progress bar
                filled = int(bar_width * percentage / 100)
                bar = '█' * filled + '-' * (bar_width - filled)

                # Display
                sys.stdout.write(
                    f"\r[{bar}] {percentage:3d}% | "
                    f"Time: {out_time} / {format_time(duration)} | "
                    f"FPS: {fps} | Speed: {speed}"
                )
                sys.stdout.flush()

                if line == 'progress=end':
                    break

    sys.stdout.write(f"\r{' ' * 150}\r")
    sys.stdout.write(
        f"\r[{'█' * 100}] 100% | Time: {format_time(duration)} / {format_time(duration)}\n"
    )
    sys.stdout.flush()

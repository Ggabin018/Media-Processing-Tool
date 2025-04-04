import sys

from utils import format_time


def progress_bar(duration:float, process):

    # Progress tracking variables
    progress_buffer = ""
    progress_info = {}

    # Create a progress bar
    bar_width = 100

    # Process output in real-time
    while process.poll() is None:
        # Read one character at a time to handle streaming
        char = process.stdout.read(1).decode('utf-8', errors='replace')
        if char == '':
            break

        progress_buffer += char

        # When we get a complete progress update (ends with \n)
        if char == '\n':
            line = progress_buffer.strip()
            progress_buffer = ""

            if '=' in line:
                key, value = line.split('=', 1)
                progress_info[key.strip()] = value.strip()

            # Check if we have a complete progress frame
            if line == 'progress=continue' or line == 'progress=end':
                # Extract useful information
                out_time = progress_info.get('out_time', '00:00:00.000000')
                fps = progress_info.get('fps', '0')
                speed = progress_info.get('speed', '0x')

                # Calculate progress percentage
                time_parts = out_time.split(':')
                current_seconds = float(time_parts[0]) * 3600 + float(time_parts[1]) * 60 + float(time_parts[2])
                percentage = min(100, int(current_seconds / duration * 100))

                # Create progress bar visualization
                filled_width = int(bar_width * percentage / 100)
                bar = '█' * filled_width + '-' * (bar_width - filled_width)

                # Print progress
                sys.stdout.write(f"\r[{bar}] {percentage:3d}% | "
                                 f"Time: {out_time[:11]} / {format_time(duration)} | "
                                 f"FPS: {fps} | Speed: {speed}")
                sys.stdout.flush()

                # Clear progress info for next update
                if line == 'progress=end':
                    break
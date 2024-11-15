import subprocess
import threading

def stream_output(stream, output_type):
    # Add color for STDERR (red) and default for STDOUT
    color_start = '\033[91m' if output_type == 'STDERR' else '\033[0m'  # Red for STDERR
    color_end = '\033[0m'
    for line in iter(stream.readline, ''):
        print(f"{color_start}[{output_type}] {line}{color_end}", end='')

def exec(command):
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    # Threads to handle stdout and stderr
    stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, 'STDOUT'))
    stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, 'STDERR'))

    stdout_thread.start()
    stderr_thread.start()

    stdout_thread.join()
    stderr_thread.join()

    process.wait()

    if process.returncode != 0:
        print(f"\nError: Command exited with status {process.returncode}")
    else:
        print("\nCommand completed successfully.")
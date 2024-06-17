import subprocess
import time
from threading import Thread
import sys
import os

def stream_output(pipe, output_func):
    """Function to continuously read from a pipe and print to the console."""
    with pipe:
        for line in iter(pipe.readline, ''):
            output_func(line.strip() + '\n')

# Define the command to run the Streamlit app
command = ["streamlit", "run", "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/RPi/models/streamlit.py"]

# Set the environment variable to ensure unbuffered output
env = os.environ.copy()
env["PYTHONUNBUFFERED"] = "1"

# Run the command with stdout and stderr redirected to pipes and unbuffered output
process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, env=env)

# Print the process ID to keep track of the running process
print(f"Started Streamlit app with PID {process.pid}")

# Create and start threads to stream stdout and stderr to the console
stdout_thread = Thread(target=stream_output, args=(process.stdout, sys.stdout.write))
stderr_thread = Thread(target=stream_output, args=(process.stderr, sys.stderr.write))

stdout_thread.start()
stderr_thread.start()

try:
    # Wait for the process to complete if necessary
    process.wait()
except KeyboardInterrupt:
    print("Stopping Streamlit app...")
    process.terminate()
    process.wait()
    print("Streamlit app stopped.")
finally:
    stdout_thread.join()
    stderr_thread.join()

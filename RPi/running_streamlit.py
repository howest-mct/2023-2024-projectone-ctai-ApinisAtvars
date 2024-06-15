# import subprocess
# import time

# # Define the command to run the Streamlit app
# command = ["streamlit", "run", "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/RPi/models/streamlit.py"]

# # Run the command with stdout and stderr redirected to pipes
# process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

# # Print the process ID to keep track of the running process
# print(f"Started Streamlit app with PID {process.pid}")

# try:
#     # Continuously read and print the output
#     while True:
#         # Read a line from stdout
#         output = process.stdout.readline()
#         if output:
#             print(output.strip())  # Print the output to the console
#         # Read a line from stderr
#         error = process.stderr.readline()
#         if error:
#             print(error.strip())  # Print the error to the console
        
#         # Optionally, add a small sleep period to reduce CPU usage
#         time.sleep(0.1)

# except KeyboardInterrupt:
#     print("Stopping Streamlit app...")
#     process.terminate()
#     process.wait()
#     print("Streamlit app stopped.")

import subprocess
import time
import threading
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
stdout_thread = threading.Thread(target=stream_output, args=(process.stdout, sys.stdout.write))
stderr_thread = threading.Thread(target=stream_output, args=(process.stderr, sys.stderr.write))

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

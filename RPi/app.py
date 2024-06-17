import socket
import threading
import time
from RPi import GPIO
from models.lcd import LCD
import subprocess
from threading import Thread
import os
import sys
import csv
import json
from repos.sql import DatabaseRepository
from services.database_service import DatabaseService
from models.custom_tkinter import DatabaseUI
from datetime import datetime

ds = DatabaseService(DatabaseRepository())

message_length = 0

previous_people_number = -1
people_number = 0


final_data = {} # Final data to input in database

HEADERSIZE = 10
new_data = True
full_message = ""

# Global vars for use in methods/threads
client_socket = None
server_socket = None
server_thread = None
shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects


def setup_socket_server():
    global server_socket, server_thread, shutdown_flag
    # Socket setup
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket instance
    server_socket.bind(('0.0.0.0', 8500)) # bind on all available ip's (WiFi and LAN), on port 8500 (this can be anything between 1024 and 65535)
    server_socket.settimeout(0.2)  # Timeout for listening, needed for loop in thread, otherwise it's blocking
    server_socket.listen(1) # enable "listening" for requests / connections


    # Start the server thread
    server_thread = threading.Thread(target=accept_connections, args=(shutdown_flag,), daemon=True) # create the thread 
                                                                               # where you wait for incoming connection
    server_thread.start() # start the above thread

def accept_connections(shutdown_flag):
    global client_socket
    print("Accepting connections")
    while not shutdown_flag.is_set():  # as long as ctrl+c is not pressed
        try:
            client_socket, addr = server_socket.accept() # accept incoming requests, and return a reference to the client and it's IP
            print("Connected by", addr)
            client_thread = threading.Thread(target=handle_client, args=(client_socket, shutdown_flag,)) # thread 
            client_thread.start() # start the above thread; where we try to accept data
        except socket.timeout: # ignore timeout errors
            pass

def handle_client(sock, shutdown_flag):
    global previous_people_number, people_number, full_message, new_data, final_data
    full_message = ""
    new_data = True

    try:
        while not shutdown_flag.is_set():
            data = sock.recv(16)  # Receive 16 bytes
            if not data:
                break  # Connection closed by client

            data = data.decode()  # Decode the message

            if new_data:  # If the data is a new message
                if len(data) >= HEADERSIZE:
                    message_length = int(data[:HEADERSIZE])  # Get the number of bytes that the message is going to be
                    new_data = False
                    full_message += data
                else:
                    continue  # Wait for the full header to be received

            else:
                full_message += data

            if len(full_message) - HEADERSIZE == message_length:  # If you've received the whole message
                content = full_message[HEADERSIZE:]  # Extract the actual content

                if 1 <= message_length <= 4:  # If its 1, 2, 3, or 4 bytes long,
                    people_number = int(content)  # assume that it's the number of people
                else:
                    # Handle potentially multiple JSON objects
                    json_objects = content.split('}{')
                    json_objects = [obj + '}' if not obj.endswith('}') else obj for obj in json_objects]
                    json_objects = ['{' + obj if not obj.startswith('{') else obj for obj in json_objects]

                    for obj in json_objects:
                        try:
                            final_data = json.loads(obj)
                        except json.JSONDecodeError as e:
                            print(f"Error decoding JSON: {e} - with object: {obj}")

                # Reset for the next message
                new_data = True
                full_message = ""

    except Exception as e:
        print(f"Exception: {e}")

    finally:
        sock.close()  # Close the socket


def write_to_csv(number_of_people):
    filename = "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/RPi/files/{}.csv".format(time.strftime("%Y-%m-%d"))
    #If a file like this^ exists, a header is not written
    if os.path.isfile(filename):
        with open(filename, "a", newline="") as csvfile: # Append to the file, set newline to empty string, because writerow() automatically appends a newline character
            writer = csv.DictWriter(csvfile, fieldnames=["Time_stamp", "Number_of_people"])
            writer.writerow({"Time_stamp": time.strftime("%H:%M:%S"), "Number_of_people": number_of_people})
    #Otherwise, it is written
    else:
        with open(filename, "a", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["Time_stamp", "Number_of_people"])
            writer.writeheader()
            writer.writerow({"Time_stamp": time.strftime("%H:%M:%S"), "Number_of_people": number_of_people})

def stream_output(pipe, output_func):
    """Function to continuously read from a pipe and print to the console."""
    with pipe:
        for line in iter(pipe.readline, ''):
            output_func(line.strip() + '\n')


###### MAIN PART ######
lcd = LCD()
lcd.display_text("Enter the class", lcd.LCD_LINE_1)
lcd.display_text("Using the GUI", lcd.LCD_LINE_2)


databaseUI = DatabaseUI(ds)
databaseUI.root.mainloop()

try:
    setup_socket_server()
    lcd.clear_display()
    lcd.display_text("Waiting for     connection...")

    while client_socket == None: # While there isn't a connection to laptop
        pass

    lcd.clear_display()
    lcd.display_text("Sending         save_line_coords")
    time.sleep(0.5) # A bit of time to display the message
    try:
        # Send whether you will use previous line coords or not
        client_socket.sendall(str(int(databaseUI.save_line_coords)).encode())
    except Exception as e:
        print(f"Failed to send save_line_coords: {e}")
    
    
    if databaseUI.save_line_coords == False: # If you want to use pre-existing line coordinates
        #Then send them to the laptop
        lcd.clear_display()
        lcd.display_text("Sending         coordinates")
        time.sleep(0.5) # A bit of time to display the message
        try:
            
            line_coords_message = f"{len(str(databaseUI.line_coords)):<10}" + str(databaseUI.line_coords)
            line_coords_message = line_coords_message.encode()
            client_socket.sendall(line_coords_message)
        except Exception as e:
            print(f"Failed to send line_coords: {e}")

    lcd.clear_display()
    lcd.display_text("People number:", lcd.LCD_LINE_1)

    while True:
        if client_socket:
            try:
                if people_number != previous_people_number:
                    lcd.display_text("                ", lcd.LCD_LINE_2)
                    lcd.display_text(str(people_number), lcd.LCD_LINE_2)
                    previous_people_number = people_number
                    write_to_csv(people_number)

            except Exception as e:
                print(f"Failed to send message: {e}")

except KeyboardInterrupt:
    print("Server shutting down")
    shutdown_flag.set() # set the shutdown flag
finally:
    server_thread.join() # join the thread, so we wait for it to finish (gracefull exit)
    server_socket.close() # make sure to close any open connections
    print(final_data)
    lcd.clear_display()
    lcd.turn_off()
    print("LCD turned off")
    GPIO.cleanup()
    print("GPIO cleaned up")


    # Adding measurements to database
    class_id = ds.get_last_class_id() if databaseUI.new_class_created == True else int(databaseUI.selected_class[0])
    date = datetime.now()
    date = date.strftime("%Y-%m-%d")
    for number, entry in enumerate(final_data['People_in']):
        ds.add_measurement(class_id, final_data['People_in'][number], final_data['People_out'][number], final_data['Timestamps'][number], date)
    print("Measurements added")
    if databaseUI.save_line_coords == True:
        ds.change_coordinates(class_id, final_data['LineStartCoords'][0], final_data['LineStartCoords'][1], final_data['EndLineCoords'][0], final_data['EndLineCoords'][1])
        print("Class coordinates added")
    
    # command_to_run_ui = ["streamlit", "run", "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/RPi/models/streamlit.py"]
    # result = subprocess.run(command_to_run_ui, capture_output=True, text=True)
    # process = subprocess.Popen(command_to_run_ui)
    # print(result.stdout)
    # print(result.stderr)
    
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

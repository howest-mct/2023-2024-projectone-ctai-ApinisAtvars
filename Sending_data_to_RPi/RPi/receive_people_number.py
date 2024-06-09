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

message_length = 0

previous_people_number = -1
people_number = 0

#TODO Get final data into this dictionary

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
    try:
        while not shutdown_flag.is_set():
            try:
                data = sock.recv(16) # Receive 16 bytes
                data = data.decode() # Decode the message

                if new_data: # If the data is a new message
                    message_length = int(data[:HEADERSIZE]) # Get the number of bytes that the message is going to be
                    new_data = False 

                full_message += data

                if len(full_message)-HEADERSIZE == message_length: # If you've received the whole message
                    if message_length == 1 or message_length == 2 or message_length==3 or message_length==4: # If its 1, 2, 3 or 4 bytes long, 
                        people_number = int(data[HEADERSIZE:]) # assume that it's the number of people
                    else:
                        final_data = json.loads(full_message)
                    new_data = True # Set new data to true again, so that the next message can be properly received
                    full_message = ""
            except Exception: # There will be an exception once the client side's code has stopped, so I just pass so that it doesn't clutter up the console
                pass
    except KeyboardInterrupt:
        pass
    finally:
        sock.close() # Close the socket


def write_to_csv(number_of_people):
    filename = "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/Sending_data_to_RPi/RPi/Files/{}.csv".format(time.strftime("%Y-%m-%d"))
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



###### MAIN PART ######

try:
    setup_socket_server()
    lcd = LCD()
    lcd.display_text("Number of people", lcd.LCD_LINE_1)

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
    # server_thread.join() # join the thread, so we wait for it to finish (gracefull exit)
    server_socket.close() # make sure to close any open connections
    lcd.clear_display()
    lcd.turn_off()
    print("LCD turned off")
    GPIO.cleanup()
    print("GPIO cleaned up")



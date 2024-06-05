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

# t = Thread(target=subprocess.run, args={"args": "cvlc v4l2:///dev/video0 --sout '#transcode{vcodec=h264,vb=1800,acodec=none}:rtp{sdp=rtsp://:8554/live.sdp}' :network-caching=50 Collapse", "shell": True})
# t.start()

previous_people_number = -1
people_number = 0


# Global vars for use in methods/threads
client_socket = None
server_socket = None
server_thread = None
shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects

# GPIO setup
BUTTON_PIN = 7

def button_callback(channel):
    global client_socket
    if client_socket: # if there is a connected client
        try:
            message = "Button Pressed!"
            client_socket.sendall(message.encode()) # send a message
        except:
            print("Failed to send message")

def setup_GPIO():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.add_event_detect(BUTTON_PIN, GPIO.FALLING, callback=button_callback, bouncetime=200)

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
    global previous_people_number, people_number
    try:
        while not shutdown_flag.is_set(): # as long as ctrl+c is not pressed
            data = sock.recv(2) # try to receive 16 bytes
            if not data: # when no data is received, try again (and shutdown flag is checked again)
                # print("No data received")
                continue # go back to top
            people_number = data.decode()
            print("Received from client:", people_number) # print the received data, or do something with it
            
            

    except socket.timeout: # capture the timeouts 
        pass
    except Exception as e:
        print(f"Error: {e}")
    finally:
        sock.close()



def write_to_csv(number_of_people):
    filename = "/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/Sending_data_to_RPi/RPi/Files/{}.csv".format(time.strftime("%Y-%m-%d"))
    #If a file like this^ exists, a header is not written
    if os.path.isfile(filename):
        with open(filename, "a", newline="") as csvfile:
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
    setup_GPIO()
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
    server_thread.join() # join the thread, so we wait for it to finish (gracefull exit)
    server_socket.close() # make sure to close any open connections
    GPIO.cleanup()
    lcd.clear_display()

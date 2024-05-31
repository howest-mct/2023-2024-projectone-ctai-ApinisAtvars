import socket
import threading
import time
import sys


server_address = ('192.168.168.167', 8500)  # Connect to RPi (or other server) on ip ... and port ... (the port is set in server.py)
# the ip address can also be the WiFi ip of your RPi, but this can change. You can print your WiFi IP on your LCD? (if needed)


# Global vars for use in methods/threads
client_socket = None
receive_thread = None
shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects


def setup_socket_client():
    global client_socket, receive_thread
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket instance
    client_socket.connect(server_address) # connect to specified server
    print("Connected to server")
#                                           Change to receive_messages for it to work again
    receive_thread = threading.Thread(target=receive_frame, args=(client_socket, shutdown_flag))
    receive_thread.start()

def receive_messages(sock, shutdown_flag):
    sock.settimeout(1)  # Set a timeout on the socket so when can check shutdown_flag.is_set in the loop, instead of blocking
    counter = 0 # count the incoming messages, part of demo
    try:
        while not shutdown_flag.is_set(): # as long as ctrl+c is not pressed
            try:
                data = sock.recv(1024) # try to receive 1024 bytes of data (maximum amount; can be less)
                if not data: # when no data is received, try again (and shutdown flag is checked again)
                    break
                print("Received from server:", data.decode()) # print the received data, or do something with it
                counter += 1 # up the count by 1
                response = "{} message(s) received".format(counter) # create a response string
                sock.sendall(response.encode()) # encode and send the data
            except socket.timeout: # when no data comes within timeout, try again
                continue
    except Exception as e:
        if not shutdown_flag.is_set():
            print(f"Connection error: {e}")
    finally:
        sock.close()

#TODO                                       WHAT IS THIS?!?!?!?

import numpy as np
import io

def decode_numpy_array_from_binary(binary_data):
    memfile = io.BytesIO(binary_data)
    memfile.seek(0)
    return np.load(memfile)

frame = np.zeros((640,640,3), np.uint8)

def receive_frame(sock, shutdown_flag):
    global frame

    sock.settimeout(1)  # Set a timeout on the socket so when can check shutdown_flag.is_set in the loop, instead of blocking
    try:
        while not shutdown_flag.is_set(): # as long as ctrl+c is not pressed
            try:
                data = sock.recv(1024) # try to receive 1024 bytes of data (maximum amount; can be less)
                if not data: # when no data is received, try again (and shutdown flag is checked again)
                    break

                data = decode_numpy_array_from_binary(data) #Decode the frame sent by raspi
                frame = data #Return this frame
            
            except socket.timeout: # when no data comes within timeout, try again
                continue
    except Exception as e:
        if not shutdown_flag.is_set():
            print(f"Connection error: {e}")
    finally:
        sock.close()

import cv2

def main():
    global client_socket, receive_thread

    setup_socket_client()

    if client_socket is None:
        print("Not connected, is server running on {}:{}?".format(server_address[0], server_address[1]))
        sys.exit()
    
    # send "hello I'm connected" message
    # client_socket.sendall("Hello from AI / notebook".encode()) # send a "connected" message from client > server
        

    try:
        while True: # random loop for other things
            cv2.imshow("Raspi camera", frame)
            print(frame)
    except KeyboardInterrupt:
        print("Client disconnecting...")
        shutdown_flag.set()
    finally:
        client_socket.close()
        receive_thread.join()
        print("Client stopped gracefully")

if __name__ == "__main__":
    main()
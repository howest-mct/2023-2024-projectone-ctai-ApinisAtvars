import socket
import threading
import time
import sys

# TODO Send also the people_in and people_out

class LaptopClient:
    def __init__(self) -> None:
        
        self.server_address = ('192.168.168.167', 8500)  # Connect to RPi (or other server) on ip ... and port ... (the port is set in server.py)
        # the ip address can also be the WiFi ip of your RPi, but this can change. You can print your WiFi IP on your LCD? (if needed)


        # Global vars for use in methods/threads
        self.client_socket = None
        self.receive_thread = None
        self.shutdown_flag = threading.Event() # see: https://docs.python.org/3/library/threading.html#event-objects
        self.data = ""
        self.previously_sent = ""

        self.message_length = 0
        
        self.HEADERSIZE = 10

    # def send_final_data(self):
    #     final_data = {
    #         'people_in': self.people_in,
    #         'people_out': self.people_out,
    #         'timestamps': self.timestamps
    #     }
    #     final_data_json = json.dumps(final_data)
    #     try:
    #         # Send the keyword indicating final data
    #         self.client_socket.sendall("final_data".encode())
    #         time.sleep(0.1)  # Slight delay to ensure the server processes the keyword first
    #         # Send the actual final data
    #         self.client_socket.sendall(final_data_json.encode())
    #     except Exception as e:
    #         print(f"Failed to send final data: {e}")

    def setup_socket_client(self):
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket instance
        self.client_socket.connect(self.server_address) # connect to specified server
        print("Connected to server")

        self.receive_thread = threading.Thread(target=self.send_messages, args=(self.client_socket, self.shutdown_flag))
        self.receive_thread.start()

    def send_messages(self, sock, shutdown_flag):
        sock.settimeout(1)
        while not shutdown_flag.is_set():
            time.sleep(0.01)
            try:
                if self.data != self.previously_sent:
                    
                    self.data = f"{len(str(self.data)):<10}" + str(self.data)
                    self.data = self.data.encode()
                    sock.sendall(self.data) # encode and send the data
                    self.previously_sent = self.data
            except socket.timeout:
                continue
        
    


    def main(self):
        self.setup_socket_client()

        if self.client_socket is None:
            print("Not connected, is server running on {}:{}?".format(self.server_address[0], self.server_address[1]))
            sys.exit()
        

        try:
            while True: # random loop for other things
                time.sleep(6)
                print("doing other things...")
        except KeyboardInterrupt:
            print("Client disconnecting...")
            self.shutdown_flag.set()
        finally:
            self.client_socket.close()
            self.receive_thread.join()
            print("Client stopped gracefully")

    if __name__ == "__main__":
        main()
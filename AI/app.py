import cv2
import math
from ultralytics import YOLO
import socket
import csv
import time
import os
import json
import numpy as np

# Import head tracker
from models.head_tracker import HeadTracker
from models.client import LaptopClient
from models.KalmanFilter import KalmanFilter

lc = LaptopClient()

# Import the model
model = YOLO(r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\small_final_FINAL\weights\best.pt")

# Start video capture
cap = cv2.VideoCapture(0)
# Set height and width of video capture
cap.set(3, 1920)
cap.set(4, 1080)

# Initialize a HeadTracker object
ht = HeadTracker()

number_of_people = 0
previous_number_of_people = -1
people_in_list = []
people_out_list = []
timestamps = []
people_in = 0
people_out = 0

all_box_coords = []
previous_centroid_coords = {}
start_counter_line = []
end_counter_line = []
counter_line_middle_point = -1  # Mean height of counter line
counter_line_is_drawn = 0


kalman_filters = {}
on_screen_for = {}



def parse_tuple_from_string(data_str): # Simple function for parsing a tuple from a string
    data_str = data_str.strip('()')
    data_list = data_str.split(',')
    parsed_data = [int(item.strip()) if item.strip().isdigit() else item.strip("'") for item in data_list]
    return tuple(parsed_data)

def mb_click(event, x, y, flags, param): # Callback function for drawing the counter line by clicking on screen
    global start_counter_line, end_counter_line, counter_line_is_drawn, counter_line_middle_point
    if counter_line_is_drawn == 0:
        if event == cv2.EVENT_LBUTTONDOWN:
            cv2.EVENT_FLAG_LBUTTON = not cv2.EVENT_FLAG_LBUTTON
            if cv2.EVENT_FLAG_LBUTTON == 1:
                end_counter_line = [x, y]
                counter_line_is_drawn = 1
                counter_line_middle_point = (start_counter_line[1] + end_counter_line[1]) / 2
            else:
                start_counter_line = [x, y]


crossing_counter = {}
frame_threshold = 12


def track_heads(all_box_coords, ht: HeadTracker): # Draws centroids of each bounding box    
    global number_of_people, people_in, people_out, on_screen_for, crossing_counter, frame_threshold

    objects = ht.update(all_box_coords) # Update centroid coordinates

    for (objectID, centroid) in objects.items():
        if objectID not in kalman_filters:
            # Initialize Kalman filter with the detected centroid
            kalman_filters[objectID] = KalmanFilter() 
            kalman_filters[objectID].correct(centroid[0], centroid[1])
            previous_centroid_coords[objectID] = (centroid[0], centroid[1])  # Initialize the previous centroid coords
            on_screen_for[objectID] = 0



        kf = kalman_filters[objectID]
        predicted = kf.predict()
        kf.correct(centroid[0], centroid[1])
        predicted_centroid = (int(predicted[0]), int(predicted[1]))
        on_screen_for[objectID] += 1

        if on_screen_for[objectID] > 5: # If the centroid has been on the screen for more than 5 frames, display it

            # text = f"ID {objectID}"
            # cv2.putText(img, text, (predicted_centroid[0], predicted_centroid[1]),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(img, predicted_centroid, 4, (255, 153, 255), -1)

            if counter_line_is_drawn == 1:
                try:
                    # If it's between the lines end points (horizontally)
                    if (predicted_centroid[0] > min(start_counter_line[0], end_counter_line[0])) and (predicted_centroid[0] < max(start_counter_line[0], end_counter_line[0])):
                        # If it's below or on the counter line (vertically), and used to be above it
                        # if objectID not in crossing_counter.keys() or crossing_counter[objectID] == None:
                        if predicted_centroid[1] >= counter_line_middle_point and previous_centroid_coords[objectID][1] < counter_line_middle_point:
                            # crossing_counter[objectID] = 0
                            # print(crossing_counter)
                            number_of_people += 1
                            people_in += 1
                        # If it's above or on the counter line (vertically), and used to be below it
                        elif predicted_centroid[1] <= counter_line_middle_point and previous_centroid_coords[objectID][1] > counter_line_middle_point:
                            # crossing_counter[objectID] = 0
                            # print(crossing_counter)
                            if number_of_people != 0:
                                number_of_people -= 1
                                people_out += 1
                    # if crossing_counter[objectID] >= 0:
                    #         #if                 a head is above the counter line        and used to be above it                                           or    vice versa
                    #     if (predicted_centroid[1] >= counter_line_middle_point and previous_centroid_coords[objectID][1] > counter_line_middle_point) or (predicted_centroid[1] <= counter_line_middle_point and previous_centroid_coords[objectID][1] < counter_line_middle_point):
                    #         crossing_counter[objectID] += 1
                    #         print(crossing_counter)
                    #         if crossing_counter[objectID] >= frame_threshold:
                    #             if predicted_centroid[1] >= counter_line_middle_point:
                    #                 number_of_people += 1
                    #                 people_in += 1
                    #                 crossing_counter[objectID] = None
                    #             else:
                    #                 if number_of_people != 0:
                    #                     number_of_people -= 1
                    #                 people_out += 1
                    #                 crossing_counter[objectID] = None
                    #     # else:
                    #     #     crossing_counter[objectID] = None # otherwise reset
                except Exception:
                    continue

        previous_centroid_coords[objectID] = predicted_centroid


def draw_bounding_box(box, img): # Draws bounding box of centroids
    global all_box_coords
    x1, y1, x2, y2 = map(int, box.xyxy[0])
    box_coords = (x1, y1, x2, y2)
    all_box_coords.append(box_coords)
    cv2.rectangle(img, (x1, y1), (x2, y2), (255, 153, 255), 3) # Change the 3 number tuple to change color
    confidence = math.ceil(box.conf[0] * 100) / 100
    org = [x1, y1]
    cv2.putText(img, f"Head {confidence}", org, cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 128, 0), 2) # Same here

lc.setup_socket_client()


##################################################################################################
#                                                                                                #
#                               START COMMUNICATION WITH RPi                                     #
#                                                                                                #
##################################################################################################


while lc.client_socket is None: # While there is no connection
    pass

save_line_coords = None # Whether to save line coords or not (boolean)
line_coords = None # Line coordinates (tuple)

while save_line_coords is None: # While save_line_coords isn't received
    try:
        save_line_coords = lc.client_socket.recv(1).decode() # Try to receive a byte of data from RPi
    except Exception as e:
        print(f"Error while receiving save_line_coords: {e}")

print(f"Save line coords? {save_line_coords}") # This is here mainly for debugging

# The following block receives line coordinates. It's only executed if the user wants to use previously saved line coords

if int(save_line_coords) == 0: # Cast it as an int, but you can also cast is as a bool
    full_message = ""
    while line_coords is None: # While line coordinates aren't received
        try:
            data = lc.client_socket.recv(1024).decode()
            if len(data) >= 10: # 10 is the length of the prefix that I use for all of my messages
                message_length = int(data[:10]) # You can cast a string with a number and infinite amount of spaces preceeding it as an int in Python
                full_message += data
            if len(full_message) - 10 == message_length:
                line_coords = parse_tuple_from_string(full_message[10:])
        except socket.timeout:
            continue
        except Exception as e:
            print(f"Error while receiving line coordinates: {e}")

print(f"Line coords: {line_coords}") # These are also printed for debugging purposes

if line_coords is not None: # If line coords are given
    start_counter_line = [line_coords[0], line_coords[1]]
    end_counter_line = [line_coords[2], line_coords[3]]
    counter_line_is_drawn = 1 # A flag used for checking whether to start counting people or not
    counter_line_middle_point = (start_counter_line[1] + end_counter_line[1]) / 2

##################################################################################################
#                                           MAIN LOOP                                            #
##################################################################################################

cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", mb_click) # Here you set the callback function to draw counter line

while True:
    ret, img = cap.read() # Capture frame

    results = model.predict(img, stream=True, iou=0.7, conf=0.5, verbose=False) # Make prediction with model

    for result in results:
        boxes = result.boxes # Get bounding boxes
        for box in boxes:
            draw_bounding_box(box, img) # Draw each box

    track_heads(all_box_coords, ht) # This draws the centroids of each head

    all_box_coords = []

    if previous_number_of_people != number_of_people: # If the number of people is different, it's sent to the RPi
        lc.data = number_of_people
        previous_number_of_people = number_of_people
        people_out_list.append(people_out) # Also, some data is saved in lists to be sent to the RPi
        people_in_list.append(people_in) #   after the main loop stops
        timestamps.append(time.strftime("%H:%M:%S"))

    if counter_line_is_drawn == 1: # If the line is drawn, display it
        cv2.line(img, start_counter_line, end_counter_line, (153, 255, 204), 2)
    else: # Otherwise, tell the user to draw it
        cv2.putText(img, "Draw counter line", (20, 80), cv2.FONT_HERSHEY_TRIPLEX, 1, (102, 102, 255), 2)

    # Display the number of people
    cv2.putText(img, "People: {}".format(str(number_of_people)), (40, 45), cv2.FONT_HERSHEY_TRIPLEX, 2, (153, 255, 255), 2)
    cv2.imshow("Webcam", img) # Show the frame

    if cv2.waitKey(1) == ord('q'):
        lc.data = json.dumps({"People_in": people_in_list, "People_out": people_out_list, "Timestamps": timestamps, "LineStartCoords": start_counter_line, "EndLineCoords": end_counter_line})
        break

time.sleep(2)
lc.shutdown_flag.set()
lc.client_socket.close()
lc.receive_thread.join()
cap.release()
cv2.destroyAllWindows()
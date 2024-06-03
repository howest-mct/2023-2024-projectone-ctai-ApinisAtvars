import gradio as gr
import numpy as np

import cv2
import math
from ultralytics import YOLO

# csv, os and time needed for writing to the csv file
import csv
import time
import os

#Import head tracker
from models.head_tracker import HeadTracker

from models.client import LaptopClient



def write_to_csv(number_of_people):
    filename = "D:/Project 1/2023-2024-projectone-ctai-ApinisAtvars/Sending_data_to_RPi/Files/{}.csv".format(time.strftime("%Y-%m-%d"))
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





def predict(img):
    lc = LaptopClient()

    model = YOLO(r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\train2_medium_new_dataset\weights\best.pt")

    ht = HeadTracker()

    number_of_people = 0
    previous_number_of_people = -1

    all_box_coords = []
    previous_centroid_coords = {}

    start_counter_line = []
    end_counter_line = []
    counter_line_middle_point = -1 #Mean height of counter line
    counter_line_is_drawn = 0

    results = model(img)
    for result in results:
        boxes = result.boxes

        for box in boxes:
            # Get bounding box coordinates
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # Convert to int values
            
            # Make a tuple of them (Used later for the counter)
            box_coords = (x1,y1,x2,y2)
            all_box_coords.append(box_coords)

            # Overlay the bounding boxes
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

            # Calculate the confidence
            confidence = math.ceil((box.conf[0]*100))/100

            # Set Object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(img, f"Head {confidence}", org, font, fontScale, color, thickness)

        # update our centroid tracker using the computed set of bounding box rectangles
        objects = ht.update(all_box_coords)

        # loop over the tracked objects
        for (objectID, centroid) in objects.items():
            # draw both the ID of the object and the centroid of the
            # object on the output frame
            text = "ID {}".format(objectID)
            cv2.putText(img, text, (centroid[0] - 10, centroid[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            cv2.circle(img, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)

            #Check if point is above counter line and between its endpoints
            if counter_line_is_drawn == 1:
                try:
                    if (centroid[0] > min(start_counter_line[0], end_counter_line[0])) and (centroid[0] < max(start_counter_line[0], end_counter_line[0])): # If it's between the line's endpoints
                        if centroid[1] > counter_line_middle_point and previous_centroid_coords[objectID][1] < counter_line_middle_point: #If it's above the line and didn't use to be
                            number_of_people += 1
                        else:
                            if centroid[1] < counter_line_middle_point and previous_centroid_coords[objectID][1] > counter_line_middle_point: #If it's below the line and didn't use to be
                                if number_of_people != 0:
                                    number_of_people -= 1
                except Exception as ex:
                    continue


            previous_centroid_coords[objectID] = centroid

        all_box_coords = []
    
    if previous_number_of_people != number_of_people:
        lc.data = number_of_people
        write_to_csv(number_of_people)
    
    previous_number_of_people = number_of_people

    if counter_line_is_drawn == 1:
        cv2.line(img, start_counter_line, end_counter_line, (0,255,0), 2)
    else:
        cv2.putText(img, "Draw counter line", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)


    # Display the amount of people
    cv2.putText(img, "People: {}".format(str(number_of_people)), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    #Show the image
    cv2.imshow("Webcam", img)

    return img

demo = gr.Interface(
    predict, 
    gr.Image(sources=["webcam"], streaming=True), 
    "image",
    live=True
)
demo.launch()
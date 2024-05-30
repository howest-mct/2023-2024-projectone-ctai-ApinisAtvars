import cv2
import math
from ultralytics import YOLO

#Import head tracker
from models.head_tracker import HeadTracker


#Import the model
model = YOLO(r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\train9\weights/best.pt")

#Define class names (I have only 1 class)
class_names = ["head"]

#Start video capture
cap = cv2.VideoCapture(1)

#Define the length and height of video capture
cap.set(3, 1920)
cap.set(4, 1200)

#Define the counter line
start_counter_line = (480, 350)
end_counter_line = (960, 350)

ht = HeadTracker()

all_box_coords = []


while True:
    #Get frame
    ret, img= cap.read()
    overlay = img.copy()

    # cv2.line(img, start_counter_line, end_counter_line, (0,0,255), 12)

    # img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)


    #Make prediction on the frame
    results = model(img, stream=True)

    for result in results:
        boxes = result.boxes




        for box in boxes:
            # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values
            
            box_coords = (x1,y1,x2,y2)
            all_box_coords.append(box_coords)

                # Overlay the bounding boxes
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # Calculate the confidence
            confidence = math.ceil((box.conf[0]*100))/100
            # print("Confidence --->",confidence)

                # Get class name
            cls = int(box.cls[0])
            # print("Class name -->", class_names[cls])

                # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(img, f"{class_names[cls]} {confidence}", org, font, fontScale, color, thickness)

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

        all_box_coords = []

    cv2.imshow('Webcam', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
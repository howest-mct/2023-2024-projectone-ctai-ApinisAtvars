import cv2
import math
from ultralytics import YOLO

#Import head tracker
from models.head_tracker import HeadTracker


#Import the model

    #Small model
model = YOLO(r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\train9_small_model_cuda\weights/best.pt")

#Define class names (I have only 1 class)
class_names = ["head"]

#Start video capture
cap = cv2.VideoCapture(0)

#Define the length and height of video capture
cap.set(3, 1920)
cap.set(4, 1200)

#Define the counter line
start_counter_line = (480, 350)
end_counter_line = (960, 350)

number_of_people = 0


ht = HeadTracker()

all_box_coords = []
previous_centroid_coords = {}

start_counter_line = []
end_counter_line = []
counter_line_is_drawn = 0

# Callback method for left mouse button
def mb_click(event,x,y,flags,param):
    print(">>>>>", event)
    global start_counter_line, end_counter_line, counter_line_is_drawn

    
    if counter_line_is_drawn == 0:
        if event == cv2.EVENT_LBUTTONDOWN: #It starts at true
            cv2.EVENT_FLAG_LBUTTON = not cv2.EVENT_FLAG_LBUTTON #I invert it
            if cv2.EVENT_FLAG_LBUTTON == 1: # If it's at 1
                end_counter_line.append(x) #These need to be in global variables, because in the main code
                end_counter_line.append(y) #I use the line end positions to perform people counting
                # cv2.line(img, start_counter_line, end_counter_line, (0,255,0), 6) # Draw the counter line
                counter_line_is_drawn = 1 # Set the counter line drawn flag, so that you can only have one counter line


            else: 
                start_counter_line.append(x)
                start_counter_line.append(y) # Else, I store the coords of this cursor position

            print(cv2.EVENT_FLAG_LBUTTON) # The first printed event is false


# Set the callback function
cv2.namedWindow("Webcam")
cv2.setMouseCallback("Webcam", mb_click)





while True:
    #Get frame
    ret, img= cap.read()
    overlay = img.copy()

    # #Draw the counter line
    # cv2.line(img, start_counter_line, end_counter_line, (0,0,255), 6)

    #Makes the line transparent
    # img = cv2.addWeighted(overlay, 0.5, img, 0.5, 0)

    #Make prediction on the frame
    results = model(img, stream=True)

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

            # Get class id
            cls = int(box.cls[0])

            # Set Object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_COMPLEX
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

            #Check if point is above counter line and between its endpoints
            if counter_line_is_drawn == 1:
                try:
                    if centroid[0] > start_counter_line[0] and centroid[0] < end_counter_line[0]: # If it's between the line's endpoints
                        if centroid[1] > end_counter_line[1] and previous_centroid_coords[objectID][1] < end_counter_line[1]: #If it's above the line and didn't use to be
                            number_of_people += 1
                        else:
                            if centroid[1] < end_counter_line[1] and previous_centroid_coords[objectID][1] > end_counter_line[1]: #If it's below the line and didn't use to be
                                if number_of_people!=0:
                                    number_of_people-=1
                except Exception as ex:
                    continue


            previous_centroid_coords[objectID] = centroid

        all_box_coords = []


    if counter_line_is_drawn == 1:
        cv2.line(img, start_counter_line, end_counter_line, (0,255,0), 2)
    else:
        cv2.putText(img, "Draw counter line", (20, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)


    # Display the amount of people
    cv2.putText(img, "People: {}".format(str(number_of_people)), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,0,255), 2)

    #Show the image
    cv2.imshow("Webcam", img)

    #If Q is pressed, end the video streaming
    if cv2.waitKey(1) == ord('q'):
        break

#Clear up everything
cap.release()
cv2.destroyAllWindows()
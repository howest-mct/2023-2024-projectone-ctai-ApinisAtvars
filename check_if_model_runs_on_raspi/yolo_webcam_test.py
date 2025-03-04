import cv2
import math
from ultralytics import YOLO

# model = YOLO(r"/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/runs/detect/train2/weights/best.pt")
model = YOLO(r"D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\small_final_FINAL\weights\best.pt")


class_names = ["head"]

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

while True:
    ret, img= cap.read()
    results = model(img, stream=True)

    for result in results:
        boxes = result.boxes

        for box in boxes:
                # bounding box
            x1, y1, x2, y2 = box.xyxy[0]
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2) # convert to int values

                # put box in cam
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 255), 3)

                # confidence
            confidence = math.ceil((box.conf[0]*100))/100
            print("Confidence --->",confidence)

                # class name
            cls = int(box.cls[0])
            print("Class name -->", class_names[cls])

                # object details
            org = [x1, y1]
            font = cv2.FONT_HERSHEY_SIMPLEX
            fontScale = 1
            color = (255, 0, 0)
            thickness = 2

            cv2.putText(img, f"{class_names[cls]} {confidence}", org, font, fontScale, color, thickness)


    cv2.imshow('Webcam', img)

    if cv2.waitKey(1) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
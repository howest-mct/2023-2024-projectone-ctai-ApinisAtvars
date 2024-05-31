import cv2
import numpy as np


def mb_click(event,x,y,flags,param):
    global ix,iy

    print(event)

    if event == cv2.EVENT_LBUTTONDOWN: #It starts at true
        cv2.EVENT_FLAG_LBUTTON = not cv2.EVENT_FLAG_LBUTTON #I invert it
        if cv2.EVENT_FLAG_LBUTTON == 1: # If it's at 1, I draw the line from previous cursor pos when it was clicked to this one
            cv2.line(img, (ix, iy), (x, y), (0,255,0), 6)


        else: ix,iy = x,y # Else, I store the coords of this cursor position

        print(cv2.EVENT_FLAG_LBUTTON) # The first printed event is false

# def rmb_click(event, x, y, flags, param):
#     if event == cv2.EVENT_RBUTTONDOWN:
#         del line

cv2.namedWindow('image')
cv2.setMouseCallback('image',mb_click) # You have to set a callback function


img = np.zeros((512,512,3), np.uint8) # Just create a black screen

ix, iy = -1,-1

while True:
    cv2.imshow("image", img) # Show the black screen
    if cv2.waitKey(10) == ord('q'):
        break
cv2.destroyAllWindows()
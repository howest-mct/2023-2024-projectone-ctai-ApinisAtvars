import cv2

# Define the RTSP URL
stream_url = 'rtsp://192.168.168.167:8554/live.sdp'

# Open the video stream
cap = cv2.VideoCapture(stream_url)

if not cap.isOpened():
    print("Error: Unable to open video stream.")
    exit()

while True:
    ret, frame = cap.read()
    if not ret:
        print("Error: Unable to read frame.")
        break

    # Perform AI analysis on the frame here
    # For now, just display the frame
    cv2.imshow('Video Stream', frame)

    # Exit on pressing 'q'
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
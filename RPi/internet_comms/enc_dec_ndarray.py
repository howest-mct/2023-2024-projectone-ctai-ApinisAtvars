#####################################################
#                                                   #
#   Trying to Encode and Decode np.ndarray objects  #
#                                                   #
#####################################################

import io
import numpy as np
import cv2

def encode_numpy_array_to_binary(array):
    memfile = io.BytesIO()
    np.save(memfile, array)
    memfile.seek(0)
    return memfile.read()

def decode_numpy_array_from_binary(binary_data):
    memfile = io.BytesIO(binary_data)
    memfile.seek(0)
    return np.load(memfile)


# read image 
image = cv2.imread('/home/user/Desktop/2023-2024-projectone-ctai-ApinisAtvars/runs/detect/train4/val_batch2_labels.jpg')
# show the image, provide window name first
cv2.imshow('Unencoded image', image)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()
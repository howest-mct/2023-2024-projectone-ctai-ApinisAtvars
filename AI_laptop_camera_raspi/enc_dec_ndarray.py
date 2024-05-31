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
image = cv2.imread(r'D:\Project 1\2023-2024-projectone-ctai-ApinisAtvars\runs\detect\train9_small_model_cuda\train_batch13220.jpg')
# show the image, provide window name first
cv2.imshow('Unencoded image', image)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()

#Encode image
img_enc = encode_numpy_array_to_binary(image)
print(img_enc)

#Decode image
img_dec = decode_numpy_array_from_binary(img_enc)

# show the image, provide window name first
cv2.imshow('Decoded image', img_dec)
# add wait key. window waits until user presses a key
cv2.waitKey(0)
# and finally destroy/close all open windows
cv2.destroyAllWindows()
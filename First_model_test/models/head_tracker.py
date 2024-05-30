#Needed for object tracking
from scipy.spatial import distance as dist
from collections import OrderedDict
import numpy as np

class HeadTracker():
    def __init__(self, maxDisappeared=50):
        
        #Counter used to assign new IDs to objects
        self.nextObjectID = 0

        #Key: ObjectId, Value: Object Coords (x,y)
        self.objects = OrderedDict()

        #Key: ObjectId, Value: number of frames object has been disappeared
        self.disappeared = OrderedDict()

        #Maximum number of frames that the object can be unrecognized before deleting it
        self.maxDisappeared = maxDisappeared
    
    def register(self, centroid):
        #Registers a new object
        #            Unique object Id     Coorinates of centroid
        self.objects[self.nextObjectID] = centroid

        #Object hasn't disappeared yet, so the value set to 0
        self.disappeared[self.nextObjectID] = 0

        #Increase the nextObjectID, so that it remains unique
        self.nextObjectID += 1
    
    def deregister(self, objectId):
        #Delete object that has disappeared for too long
        del self.objects[objectId]
        del self.disappeared[objectId]

    def update(self, rects):
        #Accepts a list of bounding boxes, assumed to be a tuple in the form (startX, startY, endX, endY)
        # check to see if the list of input bounding box rectangles is empty
        if len(rects) == 0:
            # loop over any existing tracked objects and mark them as disappeared
            for objectID in list(self.disappeared.keys()):
                self.disappeared[objectID] += 1
                # if we have reached a maximum number of consecutive frames where a given object has been marked as missing, deregister it
                if self.disappeared[objectID] > self.maxDisappeared:
                    self.deregister(objectID)
            # return early as there are no centroids or tracking info to update
            return self.objects
        		# initialize an array of input centroids for the current frame


        #If there are some objects recognized
        else:
            #Create empty numpy array
            inputCentroids = np.zeros((len(rects), 2), dtype="int")
            # loop over the bounding box rectangles
            for (i, (startX, startY, endX, endY)) in enumerate(rects):
                # use the bounding box coordinates to derive the centroid
                cX = int((startX + endX) / 2.0)
                cY = int((startY + endY) / 2.0)
                inputCentroids[i] = (cX, cY)
            # if we are currently not tracking any objects take the input
            # centroids and register each of them
            if len(self.objects) == 0:
                for i in range(0, len(inputCentroids)):
                    self.register(inputCentroids[i])
            # otherwise, are are currently tracking objects so we need to try to match the input centroids to existing object centroids
            # using Euclidean distance 
            else:
                # grab the set of object IDs and corresponding centroids
                objectIDs = list(self.objects.keys())
                objectCentroids = list(self.objects.values())
                # compute the distance between each pair of object
                # centroids and input centroids, respectively -- our
                # goal will be to match an input centroid to an existing
                # object centroid
                D = dist.cdist(np.array(objectCentroids), inputCentroids)
                # in order to perform this matching we must (1) find the smallest value in each row and then (2) sort the row
                # indexes based on their minimum values so that the row with the smallest value is at the *front* of the index list
                rows = D.min(axis=1).argsort()
                # next, we perform a similar process on the columns by finding the smallest value in each column and then sorting using the previously computed row index list
                cols = D.argmin(axis=1)[rows]


                # Initialize 2 sets, to keep track of row and column indexes already used
                usedRows = set()
                usedCols = set()
                # loop over the combination of the (row, column) index
                # tuples
                for (row, col) in zip(rows, cols):
                    # if we have already examined either the row or column value before, skip this iteration
                    if row in usedRows or col in usedCols:
                        continue
                    # otherwise, grab the object ID for the current row, set its new centroid, and reset the disappeared counter
                    objectID = objectIDs[row]
                    self.objects[objectID] = inputCentroids[col]
                    self.disappeared[objectID] = 0
                    # indicate that we have examined each of the row and column indexes, respectively
                    usedRows.add(row)
                    usedCols.add(col)
                # compute both the row and column index we have NOT yet
                # examined
                unusedRows = set(range(0, D.shape[0])).difference(usedRows)
                unusedCols = set(range(0, D.shape[1])).difference(usedCols)

                # in the event that the number of object centroids is equal or greater than the number of input centroids
                # we need to check and see if some of these objects have potentially disappeared
                if D.shape[0] >= D.shape[1]:
                    # loop over the unused row indexes
                    for row in unusedRows:
                        # grab the object ID for the corresponding row index and increment the disappeared counter
                        objectID = objectIDs[row]
                        self.disappeared[objectID] += 1
                        # check to see if the number of consecutive frames the object has been marked "disappeared" for is larger than the max amount of allowed frames
                        if self.disappeared[objectID] > self.maxDisappeared:
                            self.deregister(objectID)
                			# otherwise, if the number of input centroids is greater
                # than the number of existing object centroids we need to
                # register each new input centroid as a trackable object
                else:
                    for col in unusedCols:
                        self.register(inputCentroids[col])
            # return the set of trackable objects
            return self.objects
        
        
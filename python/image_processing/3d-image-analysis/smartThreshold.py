from imutils import contours
from skimage import measure
import tifffile as tf
import numpy as np
#import argparse
import imutils
import cv2
import xlsxwriter

#threshold: 0.0032*x*x - 0.6919*x + 65.743

z = 0

#novel thresholding method
def smartThreshold():
    global threshValue
    global thresh
    global threshTimes
    global z
    thresh = cv2.threshold(blurred, threshValue, 255, cv2.THRESH_BINARY)[1]

    thresh = cv2.erode(thresh, None, iterations=2)
    thresh = cv2.dilate(thresh, None, iterations=4)

    # perform a connected component analysis on the thresholded
    # image, then initialize a mask to store only the "large"
    # components
    labels = measure.label(thresh, connectivity=2, background=0)
    mask = np.zeros(thresh.shape, dtype="uint8")

    # loop over the unique components
    for label in np.unique(labels):
        # if this is the background label, ignore it
        if label == 0:
            continue

        # otherwise, construct the label mask and count the
        # number of pixels
        labelMask = np.zeros(thresh.shape, dtype="uint8")
        labelMask[labels == label] = 255
        numPixels = cv2.countNonZero(labelMask)

        # if the number of pixels in the component is sufficiently
        # large, then add it to our mask of "large blobs"
        if numPixels > 100 and numPixels < 1800:
            mask = cv2.add(mask, labelMask)
        elif numPixels > 50000:
            threshTimes += 1
            if threshTimes <= 30:
                blurred[labelMask == 255] -= 10 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()
        elif numPixels > 20000:
            threshTimes += 1
            if threshTimes <= 30:
                blurred[labelMask == 255] -= 5 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()
        elif numPixels > 1800:
            threshTimes += 1
            if threshTimes <= 30:
                blurred[labelMask == 255] -= 2 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()


while z < 148:
    blurred = cv2.imread("normalized{0}.jpg".format(z), 0)
    threshValue = 0.0032*z*z - 0.6919*z + 65.743
    threshTimes = 0
    thresh = cv2.threshold(blurred, threshValue, 255, cv2.THRESH_BINARY)[1]
    smartThreshold()
    print("finished layer {0}".format(z))
    cv2.imwrite("smartThreshed{0}.jpg".format(z), thresh)
    z += 10

print("Finished")

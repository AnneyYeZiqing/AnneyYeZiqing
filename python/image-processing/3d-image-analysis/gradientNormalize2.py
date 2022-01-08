#gradient normalize v2 (after incorporation into glareDetection)
import tifffile as tf
import numpy as np
import cv2
import xlsxwriter


gradH = 5 #gradient height, the height of each section of the horizonal gradient
gradW = 5 #the width of each section of the vertical gradient
h = 0 #height of the image
w = 0 #width of the image
centerAvgInt = 0
z = 0

workbook = xlsxwriter.Workbook('gradientNormalizeIntensity.xlsx')

worksheet = workbook.add_worksheet('detected_cells')
#notation: worksheet.write(row, col, "content"), row and col starts from 0
worksheet.write(0, 0, "z")
worksheet.write(0, 1, "centerAvgInt")

def calcCenterAvgInt():
    global imgUnmod
    global h
    global w
    print("w, h")
    print(w, h)
    sumFluor = 0
    pixelCount = 0
    for i in range (0, w):
        for j in range (h//2, h//2 + gradH):
            if imgUnmod[j, i] > 25: #excluding background pixels so they don't mess up avg
                sumFluor += imgUnmod[j, i]
                pixelCount += 1
                avgFluor = sumFluor/pixelCount
    return avgFluor

def calcVertAvgInt(): #vertical average intensity
    global imgUnmod
    global h
    global w
    print("w, h")
    print(w, h)
    sumFluor = 0
    pixelCount = 0
    for i in range (w//2-gradW, w//2):
        for j in range (0, h):
            if imgUnmod[j, i] > 25: #excluding background pixels so they don't mess up avg
                sumFluor += imgUnmod[j, i]
                pixelCount += 1
                avgFluor = sumFluor/pixelCount
    return avgFluor

def gradientNormalize():
    global imgUnmod
    global imgNormalized
    global z
    global centerAvgInt
    global w
    global h
    global gradH
    global gradW
    centerAvgInt = calcCenterAvgInt()
    print("z, center AvgInt")
    print (z, centerAvgInt)
    currentMH = h//2 #current mark of which (horizontal) slice it is at
    sumFluor = 0
    pixelCount = 0
    while currentMH > 0:
        #using a regular pixel-by-pixel approach
        #i in range (inclusive, exclusive)
        #step 1: calculating average intensity of a strip
        for i in range (0, w): #horizontal gradien, i = x, j = y
            for j in range (currentMH, currentMH+gradH): #a rectangle
                if imgUnmod[j, i] > centerAvgInt//4: #excluding background pixels so they don't mess up avg
                        sumFluor += imgUnmod[j, i]
                        pixelCount += 1
                        avgFluor = sumFluor/pixelCount
        #step 2: "normalize" that strip
        diff = int(centerAvgInt - avgFluor)
        for i in range (0, w): #horizontal gradien, i = x, j = y
            for j in range (currentMH, currentMH+gradH): #a rectangle
                if imgUnmod[j, i] > 0:
                    if imgNormalized[j, i] + diff < 65535 and imgNormalized[j, i] + diff >= 0: 
                        imgNormalized[j, i] = imgUnmod[j, i] + diff
        currentMH = currentMH - gradH
        sumFluor = 0
        pixelCount = 0
        avgFluor = 0

    #then, vertical gradient from center toward the right
    vertAvgInt = calcVertAvgInt() #for vertical
    currentMW = int(w/2) #current mark of which (horizontal) slice it is at
    sumFluor = 0
    pixelCount = 0
    while currentMW < (w-gradW):
        #using a regular pixel-by-pixel approach
        #i in range (inclusive, exclusive)
        #step 1: calculating average intensity of a strip
        for i in range (currentMW, currentMW+gradW): #horizontal gradien, i = x, j = y
            for j in range (0, h): #a rectangle
                if imgNormalized[j, i] > vertAvgInt//4: #excluding background pixels so they don't mess up avg
                        sumFluor += imgNormalized[j, i]
                        pixelCount += 1
                        avgFluor = sumFluor/pixelCount
        #step 2: "normalize" that strip
        diff = int(vertAvgInt - avgFluor)
        for i in range (currentMW, currentMW+gradW): #horizontal gradien, i = x, j = y
            for j in range (0, h): #a rectangle
                if imgUnmod[j, i] > 0:
                    if imgNormalized[j, i] + diff < 65535 and imgNormalized[j, i] + diff >= 0: 
                        imgNormalized[j, i] = imgNormalized[j, i] + diff
        currentMW = currentMW + gradW
        sumFluor = 0
        pixelCount = 0
        avgFluor = 0
    print("normalization complete for layer {0}".format(z))

counter = 1
while z < 148:
    imgUnmod = tf.imread('Embryo_3_w2iSIM-405-DAPI_cmle.tif', key = z)
    imgUnmod = (imgUnmod/257).astype('uint8')
    #cv2.imshow("imgUnmod", imgUnmod)
    imgNormalized = tf.imread('Embryo_3_w2iSIM-405-DAPI_cmle.tif', key = z)
    imgNormalized = (imgNormalized/257).astype('uint8')
    h = imgUnmod.shape[0] #dimensions of the image
    w = imgUnmod.shape[1]
    centerAvgInt = calcCenterAvgInt()
    #gradient normalize
    #gradientNormalize()
    print(z, centerAvgInt)
    worksheet.write(counter, 0, z)
    worksheet.write(counter, 1, centerAvgInt)
    blurred = cv2.GaussianBlur(imgNormalized, (31, 31), 0)
    key = cv2.waitKey(0)
    cv2.imwrite("normalized{0}.jpg".format(z), blurred)
    z += 10
    counter += 1
    

print("Finished")
workbook.close()

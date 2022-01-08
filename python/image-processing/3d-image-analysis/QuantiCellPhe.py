#By Ziqing Ye for Trcek Lab
#Last updated 12/20/2020

#import the necessary packages
from imutils import contours
from skimage import measure
import tifffile as tf
import numpy as np
#import argparse
import imutils
import cv2
import xlsxwriter


#the below parameters are to be empirically fine-tuned and determined
threshValue = 65 #the approximate segmentation thresh for the first slice
phenoThresh = 3
maxThreshIterations = 40
centerOffsetRange = 25 #threshold for whether two spots in adjacent z-slices are one cell

gradH = 5 #gradient height, the height of each section of the horizonal gradient
gradW = 5 #the width of each section of the vertical gradient

#the name of the output workbook
workbook = xlsxwriter.Workbook('new-pole-cells-count-40-49.xlsx')
#phenotypicCells = []


#initialize other global variables
z = 40 #the starting slice in the tiff file
cellCount = 0
phenotypeCount = 0 #in this case, "phenotype" = granule-expressing = pole cells
h = 0 #height of the image
w = 0 #width of the image
centerAvgInt = 0
currCells = []
oldCells = []
allCells = []

class Cell(object):
    def __init__(self, cZ, cX, cY, r):
        self.cZ = cZ
        self.cX = cX
        self.cY = cY
        self.nucR = r
        self.thickness = 1
        self.phenotype = False

            
def exportCellsInfo(): #save to excel, need to install and import xlsxwriter
    global allCells #seems like it is okay to fetch global values without importing so even this line isn't realy needed
    global workbook
    #importing is only required when you want to modify their values b/c without importing you are creating a local variable w/ the same name, I guess
    worksheet = workbook.add_worksheet('detected_cells')
    #notation: worksheet.write(row, col, "content"), row and col starts from 0
    worksheet.write(0, 0, "total cell number")
    worksheet.write(0, 1, len(allCells))
    worksheet.write(0, 2, "Phenotypic number")
    worksheet.write(0, 3, phenotypeCount)
    worksheet.write(0, 1, len(allCells))
    worksheet.write(1, 0, "number")
    worksheet.write(1, 1, "z")
    worksheet.write(1, 2, "cX")
    worksheet.write(1, 3, "cY")
    worksheet.write(1, 4, "r")
    worksheet.write(1, 5, "thickness")
    worksheet.write(1, 6, "phenotype")
    print("index, cell.cZ, cell.cX, cell.cY, cell.r, cell.thickness")
    for (index, cell) in enumerate(allCells):
        worksheet.write(index+2, 0, index)
        worksheet.write(index+2, 1, cell.cZ)
        worksheet.write(index+2, 2, cell.cX)
        worksheet.write(index+2, 3, cell.cY)
        worksheet.write(index+2, 4, cell.r)
        worksheet.write(index+2, 5, cell.thickness)
        worksheet.write(index+2, 6, cell.phenotype)

def checkPhenotype(cell):
    #check the fluorescent intensity around the cell region to see if it pass a certain threshold
    global imgGranule
    global h
    global w
    h = imgUnmod.shape[0]
    w = imgUnmod.shape[1]
    print("w {0}, h{1}".format(w, h))
    
    brightPixels = 0
    allPixels = 0
    global phenoThresh #threshold intensity of granules/phenotype
    #global phenotypicCells
        cellR = int (cell.nucR*cellSizeCoef)
    for i in range (-cellR, cellR+1): #go through each dimension to get nearby pixels
        #print (cell.cX+i)
        if cell.cX+i >= w or cell.cX+i < 0:
            break
        for j in range (-cellR, cellR+1): #radius left and right, up and down
            if i*i+j*j <= cellR*cellR: #circular radius
                #print(cell.cY+j)
                if cell.cY+j >= h or cell.cY+j < 0:
                    break
                allPixels += 1
                #print(imgGranule[cell.cY+j, cell.cX+i])
                if imgGranule[cell.cY+j, cell.cX+i] >= phenoThresh:
                    brightPixels += 1
    cv2.circle(imgGranule,(cell.cX, cell.cY), cellR, 255, 1) #mark the circle on the image, remember to export the image after finishing a layer
    print("bright pixels {0}, all pixels {1}".format(brightPixels, allPixels))
    if brightPixels / allPixels >= 0.20: #bright pixels more than 1/5 of the total area
        #phenotypicCells.append(cell)
        #cell.phenotype = True
        return True
    return False


#for calculating center average intensity
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


def smartThreshold():
    global threshValue
    global thresh
    global threshTimes
    global maxThreshIterations
    global z
    global blurred
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
            continue
            #mask = cv2.add(mask, labelMask)
        elif numPixels > 50000:
            threshTimes += 1
            if threshTimes <= maxThreshIterations:
                blurred[labelMask == 255] -= 10 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()
        elif numPixels > 20000:
            threshTimes += 1
            if threshTimes <= maxThreshIterations:
                blurred[labelMask == 255] -= 5 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()
        elif numPixels > 1800:
            threshTimes += 1
            if threshTimes <= maxThreshIterations:
                blurred[labelMask == 255] -= 2 #this should be okay since the thresholded part all have high pixel intensity
                smartThreshold()

#image_stack = tf.imread('Embryo_3_w2iSIM-405-DAPI_cmle.tif')
#thickness = image_stack.shape[0]

while z < 50:
    imgUnmod = tf.imread('Embryo_3_w2iSIM-405-DAPI_cmle.tif', key = z)
    imgUnmod = (imgUnmod/257).astype('uint8')
    #cv2.imshow("imgUnmod", imgUnmod)
    imgNormalized = tf.imread('Embryo_3_w2iSIM-405-DAPI_cmle.tif', key = z)
    imgNormalized = (imgNormalized/257).astype('uint8')
    h = imgUnmod.shape[0] #dimensions of the image
    w = imgUnmod.shape[1]
    imgGranule = tf.imread('Embryo_3_w1iSIM-488-GFP_cmle.tif', key = z)
    imgGranule = (imgGranule/257).astype('uint8')
    #imgGranule = cv2.normalize(imgGranule, dst=None, alpha=0, beta=255, norm_type=cv2.NORM_MINMAX)

    #gradient normalize
    gradientNormalize()#now imgNormalized is the normalized version of the current slice
    #threshValue = int(centerAvgInt * 1.224)

    
    blurred = cv2.GaussianBlur(imgNormalized, (31, 31), 0)

    # threshold the image to reveal light regions in the
    # blurred image
    threshValue = 0.0032*z*z - 0.6919*z + 65.743
    threshTimes = 0
    thresh = cv2.threshold(blurred, threshValue, 255, cv2.THRESH_BINARY)[1]
    smartThreshold()
    print ("smartThreshold for layer {0} finished".format(z))

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

    # find the contours in the mask, then sort them from left to
    # right
    cnts = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL,
                            cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)
    print('--------------1--------------')
    #print(mask.shape)
    print("mask.size")
    print(mask.size)
    #print(type(mask))
    #print(mask)
    #print("contours cnts length")
    #print(len(cnts))
    if not cnts:
        print('---------------1.1----------------------')
        print('no bright spots')
    else:
        cnts = contours.sort_contours(cnts)[0]
        print('cnts sorted')
        

    # loop over the contours
    #from cnts (contours) to cells:
    for (i, c) in enumerate(cnts):
        (x, y, w, h) = cv2.boundingRect(c)
        ((cX, cY), radius) = cv2.minEnclosingCircle(c)
        cv2.circle(imgUnmod, (int(cX), int(cY)), int(radius), (0, 0, 255), 2)
        cv2.putText(imgUnmod, ".", (int(cX), int(cY-2)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
        currCells.append(Cell(z, int(cX), int(cY), radius))

    for currCell in currCells: #currCells are single slice and temporary
        currCell.active = True #local variable that indicates whether a currCell has found its place of belonging
        for i in oldCells: #note: the cell objects or "i" stored in this are overall cells, which are long term and also belongs to allCells
            if (i.cX - currCell.cX)*(i.cX - currCell.cX) + (i.cY - currCell.cY)*(i.cY - currCell.cY) <= centerOffsetRange:
                i.thickness += 1 #add to the preexisting cell's thickness
                i.cX = (i.cX + currCell.cX)//2
                i.cY = (i.cY + currCell.cY)//2 #take average of the center coordinates
                if checkPhenotype(currCell) == True:
                    i.phenotype = True
                if currCell.r > i.r: #if the current slice of that cell has a greater radius than the old slice
                    i.r = currCell.r #save it to be the radius of the overall cell
                #cv2.putText(imgUnmod, allCells.index(i), (int(cX), int(cY-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
                currCell.active = False
                break
            #else do nothing
        #if after the for in oldCells loop this currCell still doesn't find where it belongs, make it into a new cell
        if currCell.active == True:
            if checkPhenotype(currCell) == True:
                currCell.phenotype = True
            allCells.append(currCell)
            oldCells.append(currCell)
            cv2.putText(imgUnmod, "{0}".format(allCells.index(currCell)), (int(cX), int(cY-5)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 0, 255), 2)
    #after this for loop is finished, empty the currCells list for the next round
    currCells.clear()
    #get rid of the finished cells in oldCells (Cells not continued in the past slice)
    for old in oldCells:
        if (old.cZ + old.thickness <= z):
            oldCells.remove(old)


    ### show the output image
  ###  #cv2.imshow("Image", image)
    key = cv2.waitKey(0)
  ###  #cv2.imwrite("normalized{0}.jpg".format(z), imgNormalized)
    #cv2.imwrite("newThresh{0}.jpg".format(z), thresh)
    #cv2.imwrite("newNuc{0}.jpg".format(z), imgUnmod)#circle around detected nucleus
    #cv2.imwrite("newCell{0}.jpg".format(z), imgGranule) #
    ###tf.imwrite("glare{0}.jpg".format(z), imgUnmod)
    print("Layer {0} finished".format(z))
    z = z + 1

exportCellsInfo()
workbook.close()
print("Save finished")

#Click Intensity V4 by Ziqing Ye
#Last Updated 5/31/2020
#note: This version includes a zoom-in function in addition to other functions in the previous version
#Functions include: normalization, adjustable radius, 2 modes (normal & pair mode), zooming in & out,
#recentering, as well as comment lines that highlights customizable features.

import cv2 #bgr as opposed to rgb
import numpy as np
import csv
import xlsxwriter
##import tifffile

#global variables
counter = 0
cirCount = 0
row = 1
#-----------------------vvvvvv0vvvvvv-------------------------------
r = 8 #default radius of roi, crank it up as needed
#-----------------------^^^^^^^^^^^^^-------------------------------
mode = 0 #mode 0 = regular, mode 1 = two clicks per number
right = 0 #this variable is used in mode 1 only; 0 is left, 1 is right
minV = 0 #global variable for min for normalization
maxV = 65535 #global variable for max for normalization
h = 0 #original height
w = 0 #original width
zoomFac = 1 #zoom factor
centerX = 0 #x coordinate of the center of imgDisp or dispRegion on imgUnmod
centerY = 0 #y coordinate of center

#------------------------vvvvvv1vvvvvvv------------------------------
img = cv2.imread('randomPhotowROI.tif',-1)
imgDisp = img #the image that is actually being displayed
imgUnmod = cv2.imread('randomPhotowROI.tif',-1) #the Unmodified raw image where intensity data will be taken
workbook = xlsxwriter.Workbook('Germ-granules-magenta.xlsx')
#------------------------^^^^^^^^^^^^^^------------------------------

#the workbook will be saved in the same folder as the code & the image
worksheet1 = workbook.add_worksheet('Avg intensity')

h = imgUnmod.shape[0] #dimentions of the image
w = imgUnmod.shape[1]
print(h)
print(w)
centerX = w/2
centerY = h/2

tupleL = len(list(img.shape)) #this returns 2 if grayscale and 3 if RGB
print(tupleL) #tupleL just keeps track of the image type

if tupleL == 2:
    print ('Grayscale')
    if img.dtype == "uint16": #check if the image is 16 bit grayscale (4096)
        maxV = 65535
        img = cv2.normalize(img, dst=None, alpha=0, beta=maxV, norm_type=cv2.NORM_MINMAX)
        imgDisp = cv2.normalize(img, dst=None, alpha=0, beta=maxV, norm_type=cv2.NORM_MINMAX)
        worksheet1.write(0, 3, "4095 to 65535")
elif tupleL == 3: #if RGB
    maxV = 255
    imgDisp = cv2.normalize(img, dst=None, alpha=0, beta=maxV, norm_type=cv2.NORM_MINMAX)
    print('RGB')


#initialize display
#---------------------vvvvvv2vvvvvv--------------------------
frameHeight = 650 #frame height, adjust based on computer display
#---------------------^^^^^^^^^^^^^--------------------------
scaleFac = frameHeight/imgUnmod.shape[0]
frameSize = (round(w*scaleFac), frameHeight) #a tuple
print (frameSize)
dispRegion = img[round(centerY-((h/zoomFac)/2)): round(centerY+((h/zoomFac)/2)), round(centerX-((w/zoomFac)/2)): round(centerX+((w/zoomFac)/2))]
#zoom out if image height exceeds what the screen can diplay (frameHeight)
if imgUnmod.shape[0]>frameHeight:
    print('Yes')
    imgDisp = cv2.resize(dispRegion, frameSize)
    print(imgDisp.shape[1])
    print(imgDisp.shape[0])
    cv2.imshow('image display', imgDisp)

def updateDisplay(): #to resize the display region to fit the frame
    global imgDisp
    global dispRegion
    global frameSize
    global centerX
    global centerY
    global h
    global w
    global zoomFac
    if centerY >=((h/zoomFac)/2) and centerY+((h/zoomFac)/2) <= h and centerX >=((w/zoomFac)/2) and centerX+((w/zoomFac)/2) <= w:
        dispRegion = img[round(centerY-((h/zoomFac)/2)): round(centerY+((h/zoomFac)/2)), round(centerX-((w/zoomFac)/2)): round(centerX+((w/zoomFac)/2))]
        imgDisp = cv2.resize(dispRegion, frameSize)
        cv2.imshow("image display", imgDisp)
    elif zoomFac == 1:
        dispRegion = img
        centerX = w/2
        centerY = h/2
        imgDisp = cv2.resize(dispRegion, frameSize)
        cv2.imshow("image display", imgDisp)
    else:
        print ('stuck')
        print (centerX)
        print (centerY)

def convertCoord(x,y): #Converts on screen coordinate into coodinate on imgUnmod
    #returns a tuple. get the tuple using sth like nX, nY = convertCoord(x,y)
    global w
    global h
    global zoomFac
    global scaleFac
    global centerX
    global centerY
    a = round (centerX + (x)/(zoomFac*scaleFac) - w/(2*zoomFac))
    b = round (centerY + (y)/(zoomFac*scaleFac) - h/(2*zoomFac))
    return a,b

#no need to convert radius because the circle will just be drawn on img and then shown through updateDisplay
    
    

#trackbar functions
def changeMin(x):
    global imgDisp
    global dispRegion
    global minV
    global maxV
    global tupleL
    print(x)
    minV = x
    updateDisplay()
    imgDisp = cv2.normalize(imgDisp, dst=None, alpha=x, beta=maxV, norm_type=cv2.NORM_MINMAX)
    #this works b/c in updateDisplay, imgDisp
    #has been set to dispRegion which is based off of img
    cv2.imshow("image display", imgDisp)
    #changes the Min

def changeMax(x):
    global imgDisp
    global dispRegion
    global minV
    global maxV
    print(x)
    maxV = x
    updateDisplay()
    imgDisp = cv2.normalize(imgDisp, dst=None, alpha=minV, beta=x, norm_type=cv2.NORM_MINMAX)
    cv2.imshow("image display", imgDisp)
    #changes Max

def setR(rad):
    global r
    r = rad

def setMode(m):
    global mode
    global right
    mode = m
    right = 0 #resets right to 0 after each switch
    
def setZoom(n):
    global zoomFac
    global dispRegion
    if n>0:
        zoomFac = n
    updateDisplay()
    cv2.imshow("image display", imgDisp)

def setCoordX(x):
    global centerX
    centerX = x
    updateDisplay()

def setCoordY(y):
    global centerY
    centerY = y
    updateDisplay()
    

#trackbar window
cv2.namedWindow('normalize')
cv2.createTrackbar('Min', 'normalize', 0, maxV, changeMin)
cv2.createTrackbar('Max', 'normalize', 0, maxV*2, changeMax)
cv2.createTrackbar('Radius', 'normalize', 0, r*2, setR)
cv2.createTrackbar('Mode', 'normalize', 0, 1, setMode)
cv2.createTrackbar('Zoom', 'normalize', 1, 5, setZoom)
cv2.createTrackbar('x', 'normalize', 0, w, setCoordX)
cv2.createTrackbar('y', 'normalize', 0, h, setCoordY)

cv2.setTrackbarPos('Max', 'normalize', maxV)
cv2.setTrackbarPos('Radius', 'normalize', r)
cv2.setTrackbarPos('Zoom', 'normalize', zoomFac)
cv2.setTrackbarPos('x', 'normalize', round(w/2))
cv2.setTrackbarPos('y', 'normalize', round(h/2))


#worksheet headers
#notation: worksheet.write(row, col, "content")
worksheet1.write(0, 0, "r = ") #this chunk of code writes in the spreadsheet
worksheet1.write(0, 1, r) # first row prints the radius
worksheet1.write(1, 0, "Circle") #second row = headings
worksheet1.write(1, 1, "x loc") #x coordinate of the center
worksheet1.write(1, 2, "y loc") #y coordinate of center
worksheet1.write(1, 3, "radius") #radius of each granule

if tupleL == 2:
    worksheet1.write(0, 2, "Grayscale")
    worksheet1.write(1, 4, "Intensity")
    worksheet1.write(1, 6, "x loc2")
    worksheet1.write(1, 7, "y loc2")
    worksheet1.write(1, 8, "radius2")
    worksheet1.write(1, 9, "Intensity2")
elif tupleL == 3:
    worksheet1.write(0, 3, "Colored")
    worksheet1.write(1, 4, "B") #blue intensity
    worksheet1.write(1, 5, "G") #green intensity
    worksheet1.write(1, 6, "R") #red intensity
    worksheet1.write(1, 8, "x loc2") #x coordinate of the center
    worksheet1.write(1, 9, "y loc2") #y coordinate of center
    worksheet1.write(1, 10, "radius2") #radius of each granule
    worksheet1.write(1, 11, "B2") #blue intensity
    worksheet1.write(1, 12, "G2") #green intensity
    worksheet1.write(1, 13, "R2") #red intensity   


#main function for clicking
def click_event(event, x, y, flags, param):
   # h = img.shape[0] #get's height
   # w = img.shape[1] #img.shape[1] get's you the width
    #a = [[0] * h for i in range(w)]

    
    if event == cv2.EVENT_LBUTTONDOWN:
        blue = 0 #initialize intensity
        green = 0
        red = 0
        gray = 0
        pixCounter = 0 #counter for how many pixel in the circle is counted

        global cirCount
        global r
        global tupleL
        global mode
        global right

        print (x,y)
        x, y = convertCoord(x, y)
        print ('converted')
        print (x, y)

        #summing the intensity of all pixels within the circle
        for i in range (-r, r+1): #go through each dimension to get nearby pixels
            for j in range (-r, r+1): #radius left and right, up and down
                if i*i+j*j <= r*r: #circular radius
                    if tupleL == 2:
                        gray += imgUnmod[y+j, x+i]
                    elif tupleL == 3:
                        blue += imgUnmod[y+j, x+i, 0] #add the intensity of the pixel to total intensity
                        green += imgUnmod[y+j, x+i, 1]
                        red += imgUnmod[y+j, x+i, 2]
                    pixCounter +=1  #update counter (total pixel count)
                    #print(circCounter, i, j, x+i, y+j, blue, green, red)

        if mode == 0: #normal mode, one click per number
            cirCount += 1
            print (cirCount)
            worksheet1.write(cirCount+1, 0, cirCount) #row +1 b/c row 1 is for headers
            worksheet1.write(cirCount+1, 1, x)
            worksheet1.write(cirCount+1, 2, y)
            worksheet1.write(cirCount+1, 3, r)
            if tupleL == 2:
                #-----------------------vvvvvv3vvvvvv----------------------------
                gray = gray/pixCounter #take average of intensity
                #-----------------------^^^^^^^^^^^^^----------------------------
                print(gray)
                worksheet1.write(cirCount+1, 4, gray)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                cv2.circle(imgDisp,(x,y), r, 65535, 1)
                cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                cv2.circle(img,(x,y), r, 65535, 1)
            elif tupleL == 3:
                #-----------------------vvvvvv3vvvvvv----------------------------
                blue = blue/pixCounter #take average of intensity
                green = green/pixCounter #take average of intensity
                red = red/pixCounter #take average of intensity
                #-----------------------^^^^^^^^^^^^^----------------------------
                print(blue, green, red)
                worksheet1.write(cirCount+1, 4, blue)
                worksheet1.write(cirCount+1, 5, green)
                worksheet1.write(cirCount+1, 6, red)
                font = cv2.FONT_HERSHEY_DUPLEX
                cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                cv2.circle(imgDisp,(x,y), r, (255,255,255), 1) #draw circle: the image/frame,the center of the circle, the radius, color, thickness.
                cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                cv2.circle(img,(x,y), r, (255,255,255), 1)
            updateDisplay()


        elif mode == 1: #double mode, two click under the same number
            if right == 0:
                right = (right+1)%2
                cirCount += 1
                print (cirCount)
                worksheet1.write(cirCount+1, 0, cirCount) #row +1 b/c row 1 is for headers
                worksheet1.write(cirCount+1, 1, x)
                worksheet1.write(cirCount+1, 2, y)
                worksheet1.write(cirCount+1, 3, r)
                if tupleL == 2:
                    #-----------------------vvvvvv3vvvvvv----------------------------
                    gray = gray/pixCounter #take average of intensity
                    #-----------------------^^^^^^^^^^^^^----------------------------
                    print(gray)
                    worksheet1.write(cirCount+1, 4, gray)

                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                    cv2.circle(imgDisp,(x,y), r, 65535, 1)
                    cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                    cv2.circle(img,(x,y), r, 65535, 1)

                elif tupleL == 3:
                    #-----------------------vvvvvv3vvvvvv----------------------------
                    blue = blue/pixCounter #take average of intensity
                    green = green/pixCounter #take average of intensity
                    red = red/pixCounter #take average of intensity
                    #-----------------------^^^^^^^^^^^^^----------------------------
                    print(blue, green, red)
                    worksheet1.write(cirCount+1, 4, blue)
                    worksheet1.write(cirCount+1, 5, green)
                    worksheet1.write(cirCount+1, 6, red)
                    
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                    cv2.circle(imgDisp,(x,y), r, (255,255,255), 1) #draw circle: the image/frame,the center of the circle, the radius, color, thickness.
                    cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                    cv2.circle(img,(x,y), r, (255,255,255), 1)
                updateDisplay()

            elif right == 1: #if it goes to the right, cirCount doesn't increase
                right = (right+1)%2
                print (cirCount)
                if tupleL == 2:       
                    worksheet1.write(cirCount+1, 6, x)
                    worksheet1.write(cirCount+1, 7, y)
                    worksheet1.write(cirCount+1, 8, r)
                    #-----------------------vvvvvv3vvvvvv----------------------------
                    gray = gray/pixCounter #take average of intensity
                    #-----------------------^^^^^^^^^^^^^----------------------------
                    print(gray)
                    worksheet1.write(cirCount+1, 9, gray)

                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                    cv2.circle(imgDisp,(x,y), r, 65535, 1)
                    cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, 65535, 1)
                    cv2.circle(img,(x,y), r, 65535, 1)

                elif tupleL == 3:
                    worksheet1.write(cirCount+1, 8, x)
                    worksheet1.write(cirCount+1, 9, y)
                    worksheet1.write(cirCount+1, 10, r)
                    #-----------------------vvvvvv3vvvvvv----------------------------
                    blue = blue/pixCounter #take average of intensity
                    green = green/pixCounter #take average of intensity
                    red = red/pixCounter #take average of intensity
                    #-----------------------^^^^^^^^^^^^^----------------------------
                    print(blue, green, red)
                    worksheet1.write(cirCount+1, 11, blue)
                    worksheet1.write(cirCount+1, 12, green)
                    worksheet1.write(cirCount+1, 13, red)
                    
                    
                    font = cv2.FONT_HERSHEY_DUPLEX
                    cv2.putText(imgDisp, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                    cv2.circle(imgDisp,(x,y), r, (255,255,255), 1) #draw circle: the image/frame,the center of the circle, the radius, color, thickness.
                    cv2.putText(img, str(cirCount), (x-3, y+3), font, .3, (255,255,255), 1)
                    cv2.circle(img,(x,y), r, (255,255,255), 1)

                updateDisplay()
            
        cv2.imshow("image display", imgDisp)


cv2.setMouseCallback('image display', click_event)

cv2.waitKey(0)
cv2.destroyAllWindows()
#----------------------------vvvvvvv4vvvvvvv------------------------------------------
cv2.imwrite('randomName.tif',img)
#----------------------------^^^^^^^^^^^^^^^------------------------------------------
workbook.close()


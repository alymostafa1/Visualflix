import cv2
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as p
import math
import time
import copy



def FindControur(contours):
    length = len(contours)
    print(len(contours))
    maxArea = -100
    if length > 0:
        for i in range(length):
            temp = contours[i]
            area = cv2.contourArea(temp)
            if area > maxArea:
                maxArea = area
                ci = i       
        cnt = contours[ci]
    return cnt 
    


vid = cv2.VideoCapture(0)
vid.set(3, 800)  # width=800
vid.set(4, 720)  # height=720 
if not vid.isOpened():
  print ("Could not open Camera")
  exit()
flag = 0
count_defects = 0
  
while(True):
    fgbg = cv2.createBackgroundSubtractorMOG2()
    ret, frame = vid.read()  
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5) 
    cv2.imshow('curFrame',display)
    ROI = frame[0:500, 0:300].copy() # Region of interest 
    # cv2.imshow('Current Roi', ROI)
    
    # Transform the image into grey scale image 
    grey = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (35, 35)
    blurred = cv2.GaussianBlur(grey, value, 0)

    '''
    First method to threshold
    '''
    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    '''
    Second method to threshold the hand 
    '''
    bgModel = cv2.createBackgroundSubtractorMOG2(0, 50)
    fgmask = bgModel.apply(ROI)  
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)    
    img = cv2.bitwise_and(ROI, ROI, mask=fgmask) 
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 58, 50], dtype="uint8")
    upper = np.array([30, 255, 255], dtype="uint8")
    skinMask = cv2.inRange(hsv, lower, upper)
    # skinMask = cv2.bitwise_not(skinMask)    
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    hsv_d = cv2.dilate(skinMask, kernel)    
    closing = cv2.morphologyEx(hsv_d, cv2.MORPH_CLOSE, kernel)    
    skinMask1 = copy.deepcopy(closing)
    
    # cv2.imshow('Thresholded hsv_d thresh1)
    cv2.imshow('skinMask ', closing)
        
    contours, hierarchy = cv2.findContours(skinMask1,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
    
    if len(contours) == 0 : 
        contours, hierarchy = cv2.findContours(thresh1,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
      
         
    # find contour with max area    
    cnt = max(contours, key = lambda x: cv2.contourArea(x))
    
    # create bounding rectangle around the contour (can skip below two lines)
    x, y, w, h = cv2.boundingRect(cnt)
    conto = cv2.rectangle(ROI, (x, y), (x+w, y+h), (0, 0, 255), 2)

    # finding convex hull
    hull = cv2.convexHull(cnt)

    # drawing contours
    drawing = np.zeros(ROI.shape,np.uint8)
    cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)

    # finding convex hull
    hull = cv2.convexHull(cnt, returnPoints=False)

    # finding convexity defects
    defects = cv2.convexityDefects(cnt, hull)
    count_defects = 0
    cv2.drawContours(display, contours, -1, (0, 255, 0), 3)

    # applying Cosine Rule to find angle for all defects (between fingers)
    # with angle > 90 degrees and ignore defects
                
    for i in range(defects.shape[0]):
        s,e,f,d = defects[i,0]

        start = tuple(cnt[s][0])
        end = tuple(cnt[e][0])  
        far = tuple(cnt[f][0])

        # find length of all sides of triangle
        a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
        b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
        c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

        # apply cosine rule here
        angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

            # drawing a circle on the finger tip 
        if start[1] <= 400: 
            cv2.circle(display, start , 1, [255,0,0], 5)

        # ignore angles > 90 and highlight rest with red dots
        if angle <= 90 :
            count_defects += 1
            cv2.circle(display, far, 1, [100,0,255], 5)
            if far[1]  > 400: 
                  count_defects -= 1
                  cv2.circle(display, far, 1, [0,0,0], 5)
                  
    # define actions required
    if count_defects == 0:
       cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv2.LINE_4)
       
    elif count_defects == 1:
        p.press("up")
        cv2.putText(display,"Increase volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv2.LINE_4)
        flag = 0
    elif count_defects == 2:
        p.press("down")
        cv2.putText(display,"Decrease Volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv2.LINE_4)
        flag = 0
    elif count_defects == 3:
        cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv2.LINE_4)
        flag = 0
    elif count_defects == 4 and flag == 0: 
        p.press("space")
        cv2.putText(display,"start/pause" + str(count_defects), (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, 
                (0, 255, 255), 
                2, 
                cv2.LINE_4)
        flag = 1
    
    cv2.imshow('curFrame',display)     
    print(count_defects , flag)
    if cv2.waitKey(1) & 0xFF == ord('s'): # "S" to quit 
        break
vid.release()
cv2.destroyAllWindows()
        
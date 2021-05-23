import cv2
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as p
import math
import time
import copy


vid = cv2.VideoCapture(0)
vid.set(3, 800)  # width=800
vid.set(4, 720)  # height=720 
# vid.set(cv2.CAP_PROP_BUFFERSIZE, 3)

if not vid.isOpened():
  print ("Could not open Camera")
  exit()
flag = 0
time_flag = 0
count_defects = 0
  
while(True):
    fgbg = cv2.createBackgroundSubtractorMOG2()
    ret, frame = vid.read()  
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5) 
    cv2.imshow('curFrame',display)
    ROI = frame[0:500, 0:300].copy() # Region of interest 
    ROI = frame.copy()
    # cv2.imshow('Current Roi', ROI)
    
    # Transform the image into grey scale image 
    grey = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (5, 5)
    blurred = cv2.GaussianBlur(grey, value, 0)
    
    # cv2.imshow('Blurred' ,blurred)

    '''
    First method to threshold
    '''
    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)
    
    # cv2.imshow('Thresholded' ,thresh1)
    
    '''
    Second method to threshold the hand 
    '''
    bgModel = cv2.createBackgroundSubtractorMOG2(0, 50)
    fgmask = bgModel.apply(ROI)  
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)    
    img = cv2.bitwise_and(ROI, ROI, mask=fgmask) 
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 48, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")
    skinMask = cv2.inRange(hsv, lower, upper)   
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    hsv_d = cv2.dilate(skinMask, kernel)    
    closing = cv2.morphologyEx(hsv_d, cv2.MORPH_CLOSE, kernel)    
    skinMask1 = copy.deepcopy(closing)   
    # cv2.imshow('skinMask ', skinMask)
    
    '''
    Third thresholding Method
    '''
    GThreshold = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,\
            cv2.THRESH_BINARY,11,2)  
        
    # cv2.imshow('Gaussian Threshol ', GThreshold)
    
    '''
    Fourth thresholding Method
    '''
    # Constants for finding range of skin color in YCrCb
    imageYCrCb = cv2.cvtColor(ROI,cv2.COLOR_BGR2YCR_CB)
    min_YCrCb = np.array([0,133,77],np.uint8)
    max_YCrCb = np.array([255,173,127],np.uint8)
    skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
    
    # cv2.imshow('YCRCB Thresholding', skinRegion)
    
    #'''
    # Apply Hough transform on the blurred image.
    
    detected_circles = cv2.HoughCircles(blurred, 
                    cv2.HOUGH_GRADIENT, 1, 20, param1 = 100,
                param2 = 30, minRadius = 1, maxRadius = 20)
    try:
         
        if detected_circles is not None:
           detected_circles = np.uint16(np.around(detected_circles))
           for i in detected_circles[0, :]:
                center = (i[0], i[1])                
                # circle center
                cv2.circle(blurred , center, 1, (100, 100, 100), 3)
                # circle outline
                radius = i[2]
                cv2.circle(blurred, center, radius, (255, 100, 255), 3)
        cv2.imshow('Gaussian Threshol ', blurred)
        
            #'''
    except: 
        continue 

    try:        
        contours, hierarchy = cv2.findContours(skinMask1,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
                       
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
        timer = time.time() - time_flag
        # print(timer)
        timer = 3           
        # define actions required
        if count_defects == 0 and timer > 2:
           cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
           time_flag = time.time()
           
        elif count_defects == 1 and timer > 2:
            p.press("up")
            cv2.putText(display,"Increase volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag = time.time()
        elif count_defects == 2 and timer > 2:
            p.press("down")
            cv2.putText(display,"Decrease Volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag = time.time()
        elif count_defects == 3 and timer > 2:
            cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag = time.time()
        elif count_defects == 4 and flag == 0 & timer > 2: 
            p.press("space")
            cv2.putText(display,"start/pause" + str(count_defects), (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 1
            time_flag = time.time()
    except:
        continue
    
    cv2.imshow('curFrame',display)     
    print(count_defects , flag )
    if cv2.waitKey(1) & 0xFF == ord('s'): # "S" to quit 
        break
vid.release()
cv2.destroyAllWindows()
        
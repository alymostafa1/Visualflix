import cv2
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as p
import math
import time
import copy



flag = 0
Zero_flag = 1000
time_flag = 0
time_flag_2 = 0
count_defects = 0
fake_cont = []

def countdown(t):
    while t:
        mins, secs = divmod(t, 60)
        timer = '{:02d}:{:02d}'.format(mins, secs)
        print(timer, end="\r")
        time.sleep(1)
        t -= 1
        return t 

    
def RGB_Threshold(ROI):
    bgModel = cv2.createBackgroundSubtractorMOG2(0, 50)
    fgmask = bgModel.apply(ROI)  
    kernel = np.ones((3, 3), np.uint8)
    fgmask = cv2.erode(fgmask, kernel, iterations=1)    
    img = cv2.bitwise_and(ROI, ROI, mask=fgmask) 
    
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower = np.array([0, 50, 80], dtype="uint8")
    upper = np.array([20, 255, 255], dtype="uint8")
    # lower = np.array([45, 34, 30], dtype="uint8")
    # upper = np.array([255, 229, 200], dtype="uint8")
    skinMask = cv2.inRange(hsv, lower, upper)   
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (10, 10))
    hsv_d = cv2.dilate(skinMask, kernel)    
    closing = cv2.morphologyEx(hsv_d, cv2.MORPH_CLOSE, kernel)    
    skinMask1 = copy.deepcopy(closing)
    return skinMask1

def YCrCb(ROI):
    imageYCrCb = cv2.cvtColor(ROI,cv2.COLOR_BGR2YCR_CB)
    min_YCrCb = np.array([0,133,77],np.uint8)
    max_YCrCb = np.array([255,173,127],np.uint8)
    skinRegion = cv2.inRange(imageYCrCb,min_YCrCb,max_YCrCb)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    hsv_d = cv2.dilate(skinRegion, kernel)    
    closing = cv2.morphologyEx(hsv_d, cv2.MORPH_CLOSE, kernel)
    return closing


def ContourLocator(CurrentFrame, ROI):
    
        contours, hierarchy = cv2.findContours(CurrentFrame,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
        
        # find contour with max area    
        contour = max(contours, key = lambda x: cv2.contourArea(x))
                
        # finding convex hull
        hull = cv2.convexHull(contour, returnPoints=False)
    
        # finding convexity defects
        defects = cv2.convexityDefects(contour, hull)
        
        return defects , contours , contour
    
    
def DetectAngle(defects, display, contour): 
        count_defects = 0
        # Ignore angles larger than 90 "LArger than any angle between two fingers"                     
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
    
            start = tuple(contour[s][0])
            end = tuple(contour[e][0])  
            far = tuple(contour[f][0])
    
            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
    
            # apply cosine rule here
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57
    
            # drawing a circle on the finger tip 
            # if start[1] <= 400: 
                # cv2.circle(display, start , 1, [255,0,0], 5)
    
            # ignore angles > 90 and highlight rest with red dots
            if angle <= 90:
                count_defects += 1
                # cv2.circle(display, far, 1, [100,0,255], 5)
                if far[1]  > 400: 
                      count_defects -= 1
                      # cv2.circle(display, far, 1, [0,0,0], 5)
                
        return count_defects


def ActionDetector(count_defects ,display ):
    if count_defects == 0:
        cv2.putText(display, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)

        Zero_flag = 0
    elif count_defects == 1 :
        p.press("up")
        cv2.putText(display, "Increase volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)
        flag = 0

    elif count_defects == 2:
        p.press("down")
        cv2.putText(display, "Decrease Volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)
        flag = 0
    elif count_defects == 3:
        cv2.putText(display, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)
        flag = 0
        
    elif count_defects == 4 and flag == 0:
        p.press("space")
        cv2.putText(display, "start/pause" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
                    (0, 255, 255),
                    2,
                    cv2.LINE_4)
        flag = 1
        
def HandDetection(frame, draw_contour = False, draw_thresholds = False): 
    
    flag_2 = 0
    # Eye_flag = 0
    
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5)    
    # cv2.imshow('curFrame',display.copy())
      
    ROI = frame[0:500, 0:300].copy() # Region of interest 
    ROI_2 = frame.copy()
    # cv2.imshow('Current Roi', ROI)
    
    # Transform the image into grey scale image 
    grey = cv2.cvtColor(ROI, cv2.COLOR_BGR2GRAY)

    # applying gaussian blur
    value = (5, 5)
    blurred = cv2.GaussianBlur(grey, value, 0)    
    # cv2.imshow('Blurred' ,blurred)

    '''
    First method to threshold the hand 
    '''
    # thresholdin: Otsu's Binarization method
    _, thresh1 = cv2.threshold(blurred, 127, 255,
                               cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)        
    '''
    Second method to threshold the hand 
    '''
    SkinMask = RGB_Threshold(ROI)

    
    '''
    Third Method to threshold the hand 
    '''
    GThreshold = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)          

    
    '''
    Fourth Method to threshold the hand 
    '''
    YCrCb_th = YCrCb(ROI)   

    
    if draw_thresholds == True:         
        cv2.imshow('Thresholded' ,thresh1)
        cv2.imshow('Skin RGB' ,SkinMask)
        cv2.imshow('Gaussian Threshol ', GThreshold)

    try:  
        '''
        Locating the contours in the ROI after thresholding
         '''              
        defects , contours, contour = ContourLocator(YCrCb_th, ROI)
        if draw_contour == True :
            cv2.drawContours(display, contours, -1, (0, 255, 0), 3)    
        count_defects = 0
        
        '''
        Detecting the angle of each Convex Defect and returning the number of Defects
        '''
        count_defects = DetectAngle(defects, display, contour)
    except: 
        count_defects = 10
    return count_defects , display
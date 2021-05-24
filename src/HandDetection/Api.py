import cv2
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as p
import math
import time
import copy
    
    
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
    return skinRegion


def ContourLocator(CurrentFrame, ROI):
    
        contours, hierarchy = cv2.findContours(CurrentFrame,cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE) 
                       
        # find contour with max area    
        contour = max(contours, key = lambda x: cv2.contourArea(x))
        
        # create bounding rectangle around the contour (can skip below two lines)
        x, y, w, h = cv2.boundingRect(contour)
        conto = cv2.rectangle(ROI, (x, y), (x+w, y+h), (0, 0, 255), 2)
    
        # finding convex hull
        hull = cv2.convexHull(contour)
    
        # # drawing contours
        # drawing = np.zeros(ROI.shape,np.uint8)
        # # cv2.drawContours(drawing, [contour], 0, (0, 255, 0), 0)
    
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
            if start[1] <= 400: 
                cv2.circle(display, start , 1, [255,0,0], 5)
    
            # ignore angles > 90 and highlight rest with red dots
            if angle <= 90 :
                count_defects += 1
                cv2.circle(display, far, 1, [100,0,255], 5)
                if far[1]  > 400: 
                      count_defects -= 1
                      cv2.circle(display, far, 1, [0,0,0], 5)
                # print(angle)
            
                      
        return count_defects
    
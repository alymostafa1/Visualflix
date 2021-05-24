import cv2
import numpy as np
import pyautogui as p

video_capture = cv2.VideoCapture(0)

counter = 0

while True:
    # Capture frame-by-frame
    ret, frame = video_capture.read()
    
    ##### CROP FRAME 
    #### FACE
    ROI = np.array([[(270,100),(270,300),(400,300),(400,100)]], dtype= np.int32)
    cv2.rectangle(frame, (250, 100), (430, 300), (0, 255, 0), 2)
    
    blank = np.zeros_like(frame)
    region_of_interest = cv2.fillPoly(blank, ROI, 255)
    region_of_interest_image = cv2.bitwise_and(frame, region_of_interest)
    
    ##### EYES
    ROI = np.array([[(270,200),(270,300),(400,300),(400,200)]], dtype= np.int32)    
    blank = np.zeros_like(frame)
    region_of_interest = cv2.fillPoly(blank, ROI, 255)
    region_of_interest_image = cv2.bitwise_and(frame, region_of_interest)
    
    ##### RGB SKIN BOUNDARIES USING YCbCr
    min_YCrCb = np.array([0,133,77],np.uint8)
    max_YCrCb = np.array([235,173,127],np.uint8)
    
    imageYCrCb = cv2.cvtColor(region_of_interest_image, cv2.COLOR_RGB2YCR_CB)
    skinRegionYCrCb = cv2.inRange(imageYCrCb, min_YCrCb,max_YCrCb)
    
    skinYCrCb = cv2.bitwise_and(region_of_interest_image, region_of_interest_image, mask = skinRegionYCrCb) ## WRONG
    skinRGB = cv2.cvtColor(skinYCrCb, cv2.COLOR_YCrCb2RGB)
    
    ##### FIND CONTOURS ON SKIN ONLY
    skin = cv2.cvtColor(skinYCrCb, cv2.COLOR_RGB2GRAY)
    ret, thresh = cv2.threshold(skin, 10, 255, 0)
    
    contours, hierarchy = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    
    #cv2.drawContours(frame, contours, -1, (255,0,0), 2)
    
    if len(contours) <= 40: ### EYES ARE SHUT
        counter += 1
        if counter < 40:
            continue
        else:
            counter = 0
            p.press("space")

    # Display the resulting frame
    cv2.imshow('Video', frame)
    # Quit
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything is done, release the capture
video_capture.release()
cv2.destroyAllWindows()
import cv2
import numpy as np
import matplotlib.pyplot as plt
import pyautogui as p
import math
import time
import copy
import datetime
from imutils.video import VideoStream
import argparse 
import imutils 



ap =argparse.ArgumentParser()
ap. add_argument("-v","--video", help="path to the video file" )
ap.add_argument("-a", "--min-area", type=int, default=100, help="Minimum area size")
args= vars (ap.parse_args())


#if the video cam is none we will read from the web cam 
if args.get("video", None) is None:
    vs= VideoStream(src=0).start()
    time.sleep(2.0)
    
else:
    vs= cv2.VideoCapture(args["video"])
    

#initialize the first frame 
firstframe= None 

#start looping over the frames 
while True:
    frame= vs.read()
    frame= frame if args.get("video",None) is None else frame[1]
    
    text= "no motion detected"
    #if we were not able to read anymore frames 
    if frame is None:
        break 
    
    #resize the frame , convert it to graycale and blur it 
    frame = imutils.resize(frame, width=500)
    gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
    gray=cv2. GaussianBlur(gray,(21,21),0 )
    
    #if the first frame is None, intialize it 
    if firstframe is None:
        firstframe=gray
        continue 
    
    #compute abs diff bet the curent frame and the first frame 
    frameDelta= cv2.absdiff(firstframe,gray)
    thresh =cv2.threshold(frameDelta,25, 255,cv2.THRESH_BINARY)[1]
    
    #dilate the threshold image to fill in holes, then find contours on the threshold image 
    thresh=cv2.dilate(thresh, None, iterations=2)
    cnts= cv2.findContours(thresh.copy(),cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    cnts=imutils.grab_contours(cnts)
    
    #Looping over contours 
    for c in cnts:
        #if contours is too small, ignore it 
        if cv2.contourArea(c) < args["min_area"]:
            continue
    
        #compute the bounding box of  contour, and draw it on the frame then update the text
        (x,y,w,h)=cv2.boundingRect(c)
        cv2.rectangle(frame,(x,y),(x+w,y+h),(0,255,0),2)
        text="motion is detected"
        
    
    #draw the text and the timestamp of when it happened 
    cv2.putText (frame, "Motion staqtus: {}".format(text),(10,20),cv2.FONT_HERSHEY_SIMPLEX,0.5,(0,0,255),2)
    cv2.putText(frame, datetime.datetime.now().strftime("%A %d %B %Y %I:%M:%S%p"),(10, frame.shape[0]-10),cv2.FONT_HERSHEY_SIMPLEX,0.35,(0,0,255),1)
    
    #show the frame and record 
        
    cv2.imshow("video feed", frame)
    cv2.imshow("Threshold", thresh)
    cv2.imshow("frame delta", frameDelta)
        
    key = cv2.waitKey(1) & 0xff
    
    #press q to break from loop 
    if key == ord('q'):
        break 
#clean up the camera and close open windows 
vs.stop() if args.get("video",None) is None else vs.release ()  

# vs.release ()  
cv2.destroyAllWindows()    
    
    
    
    
    
    
    
    
    
    
    
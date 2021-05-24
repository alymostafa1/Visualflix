from Api import * 






vid = cv2.VideoCapture(0)
vid.set(3, 800)  # width=800
vid.set(4, 720)  # height=720 
if not vid.isOpened():
  print ("Could not open Camera")
  exit()

flag = 0
time_flag = 0
time_flag_2 = 0
count_defects = 0
  
while(True):

    ret, frame = vid.read()  
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5) 
    
    cv2.imshow('curFrame',display)
    
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
    # cv2.imshow('Thresholded' ,thresh1)
    
    '''
    Second method to threshold the hand 
    '''
    SkinMask = RGB_Threshold(ROI)
    # cv2.imshow('Skin RGB' ,SkinMask)
    
    '''
    Third Method to threshold the hand 
    '''
    GThreshold = cv2.adaptiveThreshold(blurred,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,11,2)          
    # cv2.imshow('Gaussian Threshol ', GThreshold)
    
    '''
    Fourth Method to threshold the hand 
    '''
    YCrCb_th = YCrCb(ROI)   
    # cv2.imshow('YCRCB Thresholding', YCrCb_th)

    #'''
    try:  
        '''
        Locating the contours in the ROI after thresholding
        '''              
        defects , contours, contour = ContourLocator(SkinMask, ROI)                
        cv2.drawContours(display, contours, -1, (0, 255, 0), 3)    
        count_defects = 0
        
        '''
        Detecting the angle of each Convex Defect and returning the number of Defects
        '''
        count_defects = DetectAngle(defects, display, contour)
 
        timer_2 = int(time.time()*1000.0)

        print(timer_2 , time_flag_2)

        # define actions required
        if count_defects == 0 :
           cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
           time_flag = datetime.now().time()          
           time_flag_2 = int(time.time()*1000.0)         
        elif count_defects == 1:
            p.press("up")
            cv2.putText(display,"Increase volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag_2 = int(time.time()*1000.0)
            time_flag = datetime.now().time()
        elif count_defects == 2 :
            p.press("down")
            cv2.putText(display,"Decrease Volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag = datetime.now().time()
            time_flag_2 = int(time.time()*1000.0)
        elif count_defects == 3 :
            cv2.putText(display," ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 0
            time_flag = datetime.now().time()
            time_flag_2 = int(time.time()*1000.0)
        elif count_defects == 4 and flag == 0 : 
            p.press("space")
            cv2.putText(display,"start/pause" + str(count_defects), (50, 50),cv2.FONT_HERSHEY_SIMPLEX, 1, 
                    (0, 255, 255), 
                    2, 
                    cv2.LINE_4)
            flag = 1
            time_flag = datetime.now().time()
            time_flag_2 = int(time.time()*1000.0)
    except:
        continue
    
    cv2.imshow('curFrame',display)     
    # print(count_defects , flag )
    if cv2.waitKey(1) & 0xFF == ord('s'): # "S" to quit 
        break
vid.release()
cv2.destroyAllWindows()
        

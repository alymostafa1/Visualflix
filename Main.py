# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from Api import *
from src.HandDetection.Api import *
from src.FaceDetection.faceDetection import *
from src.FaceDetection.faceDetection2 import *

#from src.faceDetection2 import * 


vid = cv2.VideoCapture(0)
vid.set(3, 800)  # width=800
vid.set(4, 720)  # height=720 
if not vid .isOpened():
  print ("Could not open Camera")
  exit()

eye_count = 0

  
while(True):
    
    ret, frame = vid.read() 
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5)
    # cv2.imshow('curFrame',frame)
    count_defects , display  =  HandDetection(frame)  
    eye_flag  = faceDetect(frame)
    #eye_flag  = faceDetect2(frame)
   
    if count_defects == 0 and eye_flag == 1:
       print("0")   
       x = 0
          
    elif count_defects == 1 and eye_flag == 1:
        p.press("up")
        print("1")
        # cv2.putText(display, "Increase volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
        #             (0, 255, 255),
        #             2,
        #             cv2.LINE_4)
        flag = 0
        
    elif count_defects == 2 and eye_flag == 1:
        print("2")
        p.press("down")
        # cv2.putText(display, "Decrease Volume" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
        #             (0, 255, 255),
        #             2,
        #             cv2.LINE_4)
        flag = 0
        
    elif count_defects == 3 and eye_flag == 1:
        print("3")
        p.press("space") 
        # cv2.putText(display, " ", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
        #             (0, 255, 255),
        #             2,
        #             cv2.LINE_4)
        flag = 0
        
    elif (count_defects == 4 and flag == 0) or eye_flag == 0:
        if eye_flag == 0:
            if eye_count < 30:
               eye_count += 1
               print("eyesclosed")
            else:
                eye_count = 0
                p.press("space")
        
        else:    
            print("4")
            p.press("space")            
            # cv2.putText(display, "start/pause" + str(count_defects), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1,
            #             (0, 255, 255),
            #             2,
            #             cv2.LINE_4)
            flag = 1
            
    if eye_flag == 1:
        eye_count = 0
    cv2.imshow('curFrame',frame)
    #time.sleep(10)
   
    # for i in range(1000):  
    #     x = 0
       # print(str(i) + "Sec")
   
    if cv2.waitKey(1) & 0xFF == ord('s'): # "S" to quit 
        break
vid.release()
cv2.destroyAllWindows()
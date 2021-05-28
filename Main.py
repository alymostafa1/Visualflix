# import sys
# import os
# sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# from Api import *
import threaded
from src.HandDetection.Api import *
from src.FaceDetection.faceDetection import *
from src.FaceDetection.faceDetection2 import *
from src.GUI.Simple_Gui import *


window, list_player, media_list, player = layout()



vid = cv2.VideoCapture(0)
vid.set(3, 800)  # width=800
vid.set(4, 720)  # height=720 
if not vid .isOpened():
  print ("Could not open Camera")
  exit()

eye_count = 0
volume_flag = 0
closed_eye_counter = 0

  
while(True):

    ret, frame = vid.read() 
    display = cv2.rectangle(frame.copy(),(1,1),(300,720),(0,0,0),5)
    # cv2.imshow('curFrame',frame)
    count_defects , display  =  HandDetection(frame,draw_thresholds = False, draw_contour = False)  
    eye_flag  = faceDetect(frame)

   
    if count_defects == 0 and eye_flag == 1:   
        x = 0          
    elif count_defects == 1 and eye_flag == 1:
        p.press("up")
        volume_flag += 10
        player.audio_set_volume(int(volume_flag))
        window['-MESSAGE_AREA-'].update('Volume Increase')
        flag = 0
        
    elif count_defects == 2 and eye_flag == 1:
        volume_flag -= 10
        player.audio_set_volume(int(volume_flag))
        window['-MESSAGE_AREA-'].update('Volume Decrease')
        p.press("down")
        flag = 0
        
    elif count_defects == 3 and eye_flag == 1:
        p.press("space") 
        flag = 0
        
    elif (count_defects == 4 and flag == 0) or eye_flag == 0:
        if eye_flag == 0:
            if eye_count < 30:
               print(eye_count)
               eye_count += 1
               # print("eyesclosed")
            else:               
                eye_count = 0
                closed_eye_counter += 1
                list_player.pause()
                
                # if eye closed more than 5 times                
                if closed_eye_counter > 4 :                    
                    window['-MESSAGE_AREA-'].update('GoodNight sleepy Head')
                    list_player.pause()
                    list_player.stop()
                    window.close()
                    break
            # If eye is opened after being closed   
            # if closed_eye_counter > 1 and eye_count == 0:
            #     print("True")
            #     list_player.pause()
        
        else:    
            p.press("space") 
            list_player.pause()
            flag = 1
            
    if eye_flag == 1:
        eye_count = 0
    cv2.imshow('curFrame',display)
    
    # print(count_defects)
        #------------ The Event Loop ------------#
    # while True:
    event, values = window.read(timeout=10)       # run with a timeout so that current location can be updated
    if event == sg.WIN_CLOSED:
        list_player.stop()
        window.close()
        break

    if event == 'play':
        list_player.play()
    if event == 'pause':
        list_player.pause()
    if event == 'stop':
        list_player.stop()
    if event == 'next':
        list_player.next()
        list_player.play()
    if event == 'previous':
        list_player.previous()      # first call causes current video to start over
        list_player.previous()      # second call moves back 1 video from current
        list_player.play()
    if event == 'load':
        if values['-VIDEO_LOCATION-'] and not 'Video URL' in values['-VIDEO_LOCATION-']:
            media_list.add_media(values['-VIDEO_LOCATION-'])
            list_player.set_media_list(media_list)
            window['-VIDEO_LOCATION-'].update('Video URL or Local Path:') # only add a legit submit
    if event == 'exit':
        list_player.stop()
        window.close()
        break
    
        # update elapsed time if there is a video loaded and the player is playing
    if player.is_playing():
        window['-MESSAGE_AREA-'].update("{:02d}:{:02d} / {:02d}:{:02d}".format(*divmod(player.get_time()//1000, 60),
                                                                     *divmod(player.get_length()//1000, 60)))
    else:
        window['-MESSAGE_AREA-'].update('Load media to start' if media_list.count() == 0 else 'Ready to play media' )
    
    if cv2.waitKey(1) & 0xFF == ord('s'): # "S" to quit 
        list_player.stop()
        window.close()
        break
vid.release()
cv2.destroyAllWindows()
import cv2

def faceDetect(frame): #, faceCascade, eyeCascade):
    faceCascade = cv2.CascadeClassifier('H:\\kolya\\4th year\\2nd Term\\Image processing\\SmartMediaPlayer\\src\\FaceDetection\\haarcascade_frontalface_default.xml')
                                        
    eyeCascade = cv2.CascadeClassifier('H:\\kolya\\4th year\\2nd Term\\Image processing\\SmartMediaPlayer\\src\\FaceDetection\\haarcascade_eye.xml')
    # gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    try:
        # Detect face using a trained classifier
        faces = faceCascade.detectMultiScale(
            frame,
            scaleFactor=1.1,
            minNeighbors=5,
            #minSize=(30, 30),
            flags=cv2.CASCADE_SCALE_IMAGE
        )
    except:
        return 0 ## NO FACE
    
    if len(faces) == 0:
        return 0 ## NO FACE, NO EYES

    for (x, y, w, h) in faces:
        # Draw a rectangle around the face
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
        # Crop the grayscale frame to be the face area
        roi_gray = frame[y:y+h, x:x+w]
        # Crop the colored frame to be the face area
        roi_color = frame[y:y+h, x:x+w]
        # Detect the eyes using a trained classifier
        eyes = eyeCascade.detectMultiScale(roi_gray, 1.3, 5)
        
        for (ex, ey, ew, eh) in eyes:
            # print(len(eyes))
            # Draw a rectangle around the eyes
            cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
            
        if len(eyes) == 0:
            return 0 ## EYES ARE SHUT FOR A CERTAIN TIME LIMIT
        else:
            return 1 ## EYES DETECTED

# import cv2
# import pyautogui as p

# faceCascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# eyeCascade = cv2.CascadeClassifier('haarcascade_eye.xml')

# video_capture = cv2.VideoCapture(0)

# counter1 = 0
# counter2 = 0

# while True:
#     # Capture frame-by-frame
#     ret, frame = video_capture.read()
#     # Convert to grayscale
#     gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#     # Detect face using a trained classifier
#     faces = faceCascade.detectMultiScale(
#         gray,
#         scaleFactor=1.1,
#         minNeighbors=5,
#         minSize=(30, 30),
#         flags=cv2.CASCADE_SCALE_IMAGE
#     )
    
#     if len(faces) == 0:
#         counter1 += 1
#         if counter1 < 30:
#             continue
#         else:
#             counter1 = 0
#             p.press("q")

#     for (x, y, w, h) in faces:
        
#         # Draw a rectangle around the face
#         cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
#         # Crop the grayscale frame to be the face area
#         roi_gray = gray[y:y+h, x:x+w]
#         # Crop the colored frame to be the face area
#         roi_color = frame[y:y+h, x:x+w]
#         # Detect the eyes using a trained classifier
#         eyes = eyeCascade.detectMultiScale(roi_gray, 1.3, 5)
        
#         for (ex, ey, ew, eh) in eyes:
#             # Draw a rectangle around the eyes
#             cv2.rectangle(roi_color, (ex, ey), (ex+ew, ey+eh), (255, 0, 0), 2)
            
#         if len(eyes) == 0:
#             counter2 += 1
#             if counter2 < 30:
#                 continue
#             else:
#                 counter2 = 0
#                 p.press("q")
#         else: 
#             counter2=0 
                
#     # Display the resulting frame
#     cv2.imshow('Video', frame)
#     # Quit
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# When everything is done, release the capture
# video_capture.release()
# cv2.destroyAllWindows()
# -*- coding: utf-8 -*-
#armarker
import cv2
from ar_markers import detect_markers
import time
from picamera import PiCamera
from picamera.array import PiRGBArray

camera=PiCamera()
###############camera setting#####################
camera.resolution=(320,240)
camera.vflip=True
camera.hflip=True
camera.framerate=20
rawCapture=PiRGBArray(camera,size=(320,240))
time.sleep(.1)

def marker_recognition(image):
    markers=detect_markers(image)
    if len(markers)!=0:
        markerid=markers[0].id
        markers[0].highlite_marker(image)

        if markerid==114:
            print('marker detected 114(left)')

        elif markerid==1156: 
            print('marker detected 1156(right)')

for frame in camera.capture_continuous(rawCapture, format="bgr", use_video_port=True):
    image = frame.array
    rawCapture.truncate(0)
    marker_recognition(image) 
    cv2.imshow('image',image)
    key=cv2.waitKey(1)
    
    if key == ord('q'):  
        break

cv2.destroyAllWindows()
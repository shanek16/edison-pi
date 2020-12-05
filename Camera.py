from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
import time

camera=PiCamera()
camera.resolution=(320,240)
camera.vflip=True
camera.hflip=True
camera.framerate=30#20
rawCapture=PiRGBArray(camera,size=(320,240))
map1=np.load('map1.npy')
map2=np.load('map2.npy')

def Camera_calibrated():
    camera.capture(rawCapture, format="bgr")
    image = rawCapture.array
    undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
    rawCapture.truncate(0)
    return undistorted_img
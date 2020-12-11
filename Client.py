PORT = 8000
import RPi.GPIO as GPIO
from http.client import HTTPConnection
import json
from time import sleep
import numpy as np
import cv2
import time
#from Time import Time
from sys import argv
from ImageRW import UploadNumpy
from picamera import PiCamera
from picamera.array import PiRGBArray
#from Camera import Camera_calibrated

def drive(left, right):
	left = np.clip(left, -100 , 100)
	right = np.clip(right, -100, 100)

	if left > 0:
		left_f = left
		left_b = 0
	else:
		left_f = 0
		left_b = -left
		
	if right > 0:
		right_f = right
		right_b = 0
	else:
		right_f = 0
		right_b = -right
	#print(left_f, left_b, right_f, right_b)
	time.sleep(0.00001)
	p1A.ChangeDutyCycle(left_f)
	p1B.ChangeDutyCycle(left_b)
	p2A.ChangeDutyCycle(right_f)
	p2B.ChangeDutyCycle(right_b)

# gpio pin setting
motor1A = 16
motor1B = 18
motor2A = 24
motor2B = 22

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1A,GPIO.OUT)
GPIO.setup(motor1B,GPIO.OUT)
GPIO.setup(motor2A,GPIO.OUT)
GPIO.setup(motor2B,GPIO.OUT)
p1A = GPIO.PWM(motor1A, 500)
p1B = GPIO.PWM(motor1B, 500)
p2A = GPIO.PWM(motor2A, 500)
p2B = GPIO.PWM(motor2B, 500)
p1A.start(0)
p1B.start(0)
p2A.start(0)
p2B.start(0)

camera=PiCamera()
camera.resolution=(320,240)
camera.vflip=True
camera.hflip=True
camera.framerate=30#20
rawCapture=PiRGBArray(camera,size=(320,240))
map1=np.load('map1.npy')
map2=np.load('map2.npy')

print(argv)
# tb=0
def main():
	# global tb
	for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):
		try:
			image = frame.array
			undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
			rawCapture.truncate(0)
			# image=Camera_calibrated()
			# te=time.time()-tb
			# print('time elapsed: ',te)
			# tb=time.time()
			motor_result = UploadNumpy(argv[1], PORT, undistorted_img)
			data = json.loads(motor_result)
			left=data['left']
			right=data['right']
			print('data[left]: ',left)
			print('data[right]: ',right)
			drive(left,right)
		except ConnectionRefusedError as error:
			print(error)
			sleep(1)
			continue

main()
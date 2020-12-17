PORT = 8000
import RPi.GPIO as GPIO
from http.client import HTTPConnection
import json
from time import sleep
import numpy as np
import cv2
import time
import sys
#from sys import argv
import argparse
from ImageRW import UploadNumpy
from picamera import PiCamera
from picamera.array import PiRGBArray

#region: argument parsing
parser=argparse.ArgumentParser()
parser.add_argument('--frame', type=int, required=False, default=30)
parser.add_argument('--ip', type=str, required=False, default='192.168.0.6')
args=parser.parse_args()
frame_rate=args.frame
ip_address=args.ip
#endregion

#region: gpio pin setting
motor1A = 16
motor1B = 18
motor2A = 24
motor2B = 22
GPIO_TRIGGER = 10
GPIO_ECHO    = 12

GPIO.setmode(GPIO.BOARD)
GPIO.setup(motor1A,GPIO.OUT)
GPIO.setup(motor1B,GPIO.OUT)
GPIO.setup(motor2A,GPIO.OUT)
GPIO.setup(motor2B,GPIO.OUT)
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)

GPIO.output(GPIO_TRIGGER, False)
p1A = GPIO.PWM(motor1A, 500)
p1B = GPIO.PWM(motor1B, 500)
p2A = GPIO.PWM(motor2A, 500)
p2B = GPIO.PWM(motor2B, 500)
p1A.start(0)
p1B.start(0)
p2A.start(0)
p2B.start(0)
#endregion

#region: camera setting
map1=np.load('map1.npy')
map2=np.load('map2.npy')
camera=PiCamera()
camera.resolution=(320,240)
camera.vflip=True
camera.hflip=True
camera.framerate=frame_rate
rawCapture=PiRGBArray(camera,size=(320,240))
#endregion

def drive(left, right):
	left = np.clip(left, -100 , 100)
	right = np.clip(right, -100, 100)
	print(left,right)

	if left > 0:
		left_f = np.clip(left,30,100)
		left_b = 0
	elif left ==0:
		left_f = 0
		left_b = 0
	else:
		left_f = 0
		left_b = -np.clip(left,-100,-30)
		
	if right > 0:
		right_f = np.clip(right,30,100)
		right_b = 0
	elif right ==0:
		right_f = 0
		right_b = 0
	else:
		right_f = 0
		right_b = -np.clip(right,-100,-30)
	print(left_f, left_b, right_f, right_b)
	time.sleep(0.00001)
	p1A.ChangeDutyCycle(left_f)
	p1B.ChangeDutyCycle(left_b)
	p2A.ChangeDutyCycle(right_f)
	p2B.ChangeDutyCycle(right_b)

def measure():
    GPIO.output(GPIO_TRIGGER, True)
    #time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
    start = time.time()
    timeOut = start

    while GPIO.input(GPIO_ECHO)==0:
        start = time.time()
        if time.time()-timeOut > 0.05:
            return 100

    while GPIO.input(GPIO_ECHO)==1:
        if time.time()-start > 0.05:
            return 100
        stop = time.time()

    elapsed = stop-start
    distance = (elapsed * 34300)/2
    print('distance: ',distance)
    return distance

tb=0
def main():
	global tb
	for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True):
		try:
			# print('camera.framerate: ',camera.framerate)
			image = frame.array
			undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
			rawCapture.truncate(0)
			te=time.time()-tb
			print('time elapsed: ',te)
			tb=time.time()
			motor_result = UploadNumpy(ip_address, PORT, undistorted_img)
			# motor_result = UploadNumpy(argv[1], PORT, undistorted_img)
			data = json.loads(motor_result)
			left=data['left']
			right=data['right']
			second=data['second']

			distance=measure()
			if distance<20:
				left=0
				right=0

			drive(left,right)
			if second >0:
				print('sleeping for {} seconds..'.format(second))
				time.sleep(second)
		except ConnectionRefusedError as error:
			print(error)
			sleep(1)
			continue
		except KeyboardInterrupt:
			GPIO.cleanup()
			sys.exit()	

main()
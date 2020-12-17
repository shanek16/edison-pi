import RPi.GPIO as GPIO
from picamera import PiCamera
from picamera.array import PiRGBArray
import numpy as np
import cv2
import time
from datetime import datetime
import os
from decision import decision
import argparse
#import linecache#?

#input white: default 150
parser=argparse.ArgumentParser()
parser.add_argument('--white', type=int, required=False, default=150)
args=parser.parse_args()
white=args.white

#image saving directory
directory='./images/image_'+datetime.now().strftime('%y%b%d%H%M%S')
pi_directory='./images/pi_image_'+datetime.now().strftime('%y%b%d%H%M%S')

#region camera setting
camera=PiCamera()
camera.resolution=(320,240)
camera.vflip=True
camera.hflip=True
camera.framerate=30#20
rawCapture=PiRGBArray(camera,size=(320,240))
map1=np.load('map1.npy')
map2=np.load('map2.npy')
image_num=0 
#time.sleep(.1)
#endregion

def select_white(image, white):
    lower = np.uint8([white,white,white])
    upper = np.uint8([255,255,255])#pure white
    white_mask = cv2.inRange(image, lower, upper)#lower~upper preserve, others->0(black)
    return white_mask

#region motor setting
motor1A = 16
motor1B = 18
motor2A = 24
motor2B = 22

chlist=(motor1A,motor1B,motor2A,motor2B)
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
result=(0,0)
#pre_result=(0,0)
#endregion

def drive(left, right):
	left = np.clip(left, -100 , 100)
	right = np.clip(right, -100, 100)
	print(left,right)

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
	print(left_f, left_b, right_f, right_b)
	#time.sleep(0.00001)
	p1A.ChangeDutyCycle(left_f)
	p1B.ChangeDutyCycle(left_b)
	p2A.ChangeDutyCycle(right_f)
	p2B.ChangeDutyCycle(right_b)
# tb=0
if __name__ == '__main__':
	for frame in camera.capture_continuous(rawCapture,format='bgr',use_video_port=True): 
		image=frame.array
		rawCapture.truncate(0)
		# te=time.time()-tb
		# print('time elapsed: ',te)
		# tb=time.time()
		undistorted_img = cv2.remap(image, map1, map2, interpolation=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT)
		pi_image=select_white(undistorted_img,white)

		result,second=decision(pi_image,undistorted_img)
		cv2.putText(undistorted_img,'({0},{1})'.format(int(result[0]),int(result[1])),(190,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
		cv2.imshow('image',undistorted_img)
		cv2.imshow('pi_image',pi_image)
		#region image save
		'''image_name='image_'+"{0:0=2d}".format(image_num)+'.png'
		image_num+=1
		try:
			os.makedirs(directory)
			os.makedirs(pi_directory)
		except OSError:
			pass
		path=os.path.join(directory, image_name)
		pi_path=os.path.join(pi_directory, image_name)
		cv2.imwrite(path,undistorted_img)
		cv2.imwrite(pi_path,pi_image)'''
		#endregion
		
		drive(result[0],result[1])
		if second >0:
			print('sleeping for {} seconds..'.format(second))
			time.sleep(second)

		key=cv2.waitKey(1)
		if key == ord('q'):  
			break
	cv2.destroyAllWindows()

	GPIO.cleanup()
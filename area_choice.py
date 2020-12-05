import numpy as np
import cv2
#import time
#import linecache
#import sys

PGAIN=1/85
# DGAIN=1

def area_choice(pi_image,image,upper_limit):#black and white pi_image only
    height,width=pi_image.shape
    pi_image= pi_image[height-upper_limit:,:]
    height = upper_limit-1
    center=160
    left=0
    right=320

    cv2.line(image,(0,upper_limit),(319,upper_limit),(0,0,255),2)
    
    if pi_image[height][:center].min(axis=0)==255:
        left=0  
    else:
        left = pi_image[height][:center].argmin(axis=0)

    if pi_image[height][center:].max(axis=0)==0:
        right=width
    else: 
        right = center+pi_image[height][center:].argmax(axis=0)
    center = int((left+right)/2)

    cv2.line(image,(left,0),(left,239),(0,0,255),2)
    cv2.line(image,(right,0),(right,239),(0,0,255),2)
    cv2.line(image,(center,0),(center,239),(0,0,255),2)

    pi_image= np.flipud(pi_image)
    mask = pi_image!= 0
    
    integral=np.where(mask.any(axis=0), mask.argmax(axis=0), height)
    left_sum = np.sum(integral[left:center])
    right_sum = np.sum(integral[center:right])
    forward_sum = np.sum(integral[center-50:center+50])

    cv2.line(image,(center-50,0),(center-50,239),(0,0,255),2)
    cv2.line(image,(center+50,0),(center+50,239),(0,0,255),2)
    cv2.putText(image,'f({0})'.format(int(forward_sum)),(190,60),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
    cv2.putText(image,'l({0})'.format(int(left_sum)),(190,90),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
    cv2.putText(image,'r({0})'.format(int(right_sum)),(190,120),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)

    speed=forward_sum/105
    # print(int(speed))
    # speed=65
    r_l=(right_sum-left_sum)
    control=PGAIN*r_l
    cv2.putText(image,'speed:{0}'.format(int(speed)),(30,60),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)
    cv2.putText(image,'control:{0}'.format(int(control)),(30,90),cv2.FONT_HERSHEY_SIMPLEX,1,(0,255,0),2)

    right_result=(speed-control)/2 #50+40=90
    left_result=(speed+control)/2  #50-40=10
    result=(left_result,right_result)
    return result
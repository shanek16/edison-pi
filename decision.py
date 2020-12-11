#from direction_choice import *
from area_choice import *
from marker_recognition import *
from stop_detection import stop_detection
from us_sensor import measure
def decision(pi_image,undistorted_img):

    result=area_choice(pi_image,undistorted_img,upper_limit=120)
    result=marker_recognition(pi_image,undistorted_img,result,speed=50)#upadate result
    result,mode=stop_detection(undistorted_img,result)
    distance=measure()
    if distance<20:
        result=(0,0)
    pre_result=result
    return result,mode
#to be imported to direction.py
import time
import cv2
import numpy as np
import linecache
import sys
PGAIN=1

def first_nonzero(arr,axis,invalid_val=-1):
    arr=np.flipud(arr)
    mask=arr!=0#??
    return np.where(mask.any(axis=axis),mask.argmax(axis=axis),invalid_val)

#############print error message for try:except #######################
# def PrintException():#skip 
    exc_type, exc_obj, tb = sys.exc_info()
    f = tb.tb_frame
    lineno = tb.tb_lineno
    filename = f.f_code.co_filename
    linecache.checkcache(filename)
    line = linecache.getline(filename, lineno, f.f_globals)
    print ('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))

################################################################

forward_limit=80
forward_m_limit=0.5
turn_m_limit=0.10
t_duty=70

def direction_choice(pi_image,image,duty,motor,pre_result):#black and white pi_image only
        height,width=pi_image.shape
        height=height-1 #319
        width=width-1 #239
        left=0
        right=width
        center=int((left+right)/2)
        
        # try:
        left=0 if pi_image[height][:center].min(axis=0)==255 else pi_image[height][:center].argmin(axis=0)
        #if lowest row left half are filled with lane left=0 
        #else left is index where lane ends(if left contains both lane and path)      
        right=width if pi_image[height][center:].max(axis=0)==0 else center+pi_image[height][center:].argmax(axis=0)
        #if right half contatins no lane right=width(max) 
        #else right is index of original width pi_image where lane starts(if right contains both lane and path)           
        center=int((left+right)/2)
        #new center
        forward=max(int(first_nonzero(pi_image[:,center],0,height))-1,0)
        #where lane blocks forward
        left_line=first_nonzero(pi_image[height-forward:height,center:],1,width-center)
        right_line=first_nonzero(np.fliplr(pi_image[height-forward:height,:center]),1,center)
        
        center_y=(np.ones(forward)*2*center-left_line+right_line)/2-center
        center_x=np.vstack((np.arange(forward),np.zeros(forward)))
        m,c=np.linalg.lstsq(center_x.T,center_y,rcond=0)[0]
        x1=center
        y1=height
        x2=np.where(m>0,width,0)
        y2=int(abs(m)*width/2)
        cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)
        cv2.putText(image,'{0}'.format(m),(190,30),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        # ############################pid
        # i_pid = i_pid + m_e * dt;
        # d_pid = (m_e - m_e_b)/ dt;
        # control = m_e* PGAIN + i_pid * IGAIN + d_pid * DGAIN
        '''if abs(m) <forward_m_limit and forward>forward_limit:
            control = m* PGAIN
            result=(duty+control,duty-control)
        else:
            result=(0,0)'''
        ########################################
        if abs(m) <forward_m_limit and forward>forward_limit:#abs(m)<0.4 forward>70 abs<0.05 and forward<100 m>0.2
            result=(duty,duty)
        elif m>=turn_m_limit:
            result=(-t_duty,t_duty) 
        elif m<=-turn_m_limit: 
            result=(t_duty,-t_duty)  
        else:
            result=(-t_duty,-t_duty)
        #forward left right 
        # print('m= {0} forward ={1}'.format(m,forward))
        return result
        # except:
        #     # PrintException()#PrintException exists in rasptest.py
        #     result=(-pre_result[0],-pre_result[1])#backward
        #     motor(result[0],result[1])
        #     time.sleep(0.3)
        #     cv2.putText(image,'in except',(160,30),cv2.FONT_HERSHEY_SIMPLEX,1,(255,0,0),2)
        #     # motor(-t_duty,-t_duty)
        #     # time.sleep(0.3)
        #     m=0
        #     # print('m= {0} forward ={1}'.format(m,forward))
        #     return result
        

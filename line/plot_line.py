import numpy as np
import cv2

image = cv2.imread('./image.png',cv2.IMREAD_COLOR)

x1=160
y1=240
x2=320
y2=0
cv2.line(image,(x1,y1),(x2,y2),(0,0,255),2)

cv2.imshow('image',image)
cv2.waitKey(0)
cv2.destroyAllWindows()

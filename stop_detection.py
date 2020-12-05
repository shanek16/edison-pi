import cv2

def stop_detection(image,result):
    mode=0
    obj = cv2.CascadeClassifier('stopsign.xml')
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    cascade_obj = obj.detectMultiScale(
        gray,
        scaleFactor=1.02,
        minNeighbors=8,
        minSize=(16,16),           
    )

    for (x_pos, y_pos, width, height) in cascade_obj:
        if(width>=40):
            cv2.rectangle(image, (x_pos, y_pos), (x_pos+width, y_pos+height), (255, 255, 255), 2)
            cv2.putText(image, 'Stop', (x_pos, y_pos-10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            mode=mode+1#stop
            # print(mode)
    if mode>2:
        result=(0,0)
    else:
        result=result       
    return result,mode
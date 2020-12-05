file = 'steveholt.jpg'

from http.client import HTTPConnection
import numpy as np
import cv2


def Upload(body, host, headers={}):
    conn = HTTPConnection(host)
    conn.request('POST', '/', body=body, headers=headers)
    res = conn.getresponse()
    print(res.getheaders())
    print(res.getheader('X-Server2Client', 'Fallback'))
    print('Uploaded to', host, 'with status', res.status)
    motor_result=res.read()
    #read from processed image

    #json(string)-->dictionary    
    return motor_result

def Download():
    with open(file, 'wb') as File:
        conn = HTTPConnection('www.mixedcontentexamples.com')
        conn.request("GET", "/Content/Test/steveholt.jpg")
        res = conn.getresponse()
        File.write(res.read())
        print('Downloaded to', file)


def DownloadAndUpload():
    Download()
    with open(file, 'rb') as File:
        Upload(File.read())


def UploadNumpy(host, port, image):
    #image = 255 * np.random.random((100, 100, 3))
    #print('shape', image.shape)
    result, encoded_image = cv2.imencode('.jpg', image,
                               [int(cv2.IMWRITE_JPEG_QUALITY), 90])
    if not result:
        raise Exception('Image encode error')
    host += ":" + str(port)
    motor_result=Upload(encoded_image.tobytes(), host, {"X-Client2Server": "123"})
    return motor_result

if __name__ == '__main__':
    # Download()
    #DownloadAndUpload()
    host = '192.168.0.3'
    port = 8000
    UploadNumpy(host, port)

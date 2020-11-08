import cv2
import numpy as np
from matplotlib import pyplot as plt
face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml') #haarcascade_frontalface_default.xml이 xml은 같은 디렉토리안에 있어야함.
cap = cv2.VideoCapture(0)

face_x = 0
face_y = 0

def VidFaceCap():
    while (True):
        ret, img = cap.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        face = face_cascade.detectMultiScale(gray, 1.3, 5)
        for (x, y, w, h) in face:
            print("Detected faces : " + str(face.shape[0]))
            if(face.shape[0] <= 1):
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
                face_x, face_y = x,y
                print(face_x, face_y) # 얼굴(사각형) 좌표점
            else:
                print("여러명입니다. 한 명씩 검사해주세요.");
                cv2.rectangle(img, (x, y), (x + w, y + h), (255, 0, 0), 2)
        cv2.imshow('frame', img)
        if cv2.waitKey(1) & 0xFF == ord('q'): # 종료
            break
    cap.release() # cap닫기
VidFaceCap()

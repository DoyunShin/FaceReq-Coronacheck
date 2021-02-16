# -*- coding:utf8 -*-
#! /usr/bin/python3

# import the necessary packages
from imutils.video import VideoStream
from imutils.video import FPS
import face_recognition
import imutils
import pickle
import time
import cv2
import numpy
import os
import requests
from pyzbar import pyzbar
from datetime import datetime

from smbus2 import SMBus
from Adafruit_AMG88xx import Adafruit_AMG88xx
from mlx90614 import MLX90614
from thermal_image import thermal_draw
from PIL import ImageFont, ImageDraw, Image

face_classifier = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')

def write_hangul_text(frame, bgImg, PText ):
	# 한글 Text 쓰기
	# text 배경이미지는 사전에 불러와서 파라메타로 넘겨야함...
	# bgImg = Image.open('text_bg.jpg')
	# 글자색과 폰트
	b,g,r,a = 255,255,255,0
	#각 OS경로에 맞게....
	fontpath = "/usr/share/fonts/truetype/namum/NanumGothic.ttf"
	font = ImageFont.truetype(fontpath, 30)

	# 카메라이미지 변환
	img_pil = Image.fromarray(frame)
	# 카메라 capture 크기 확인
	xLen, yLen = img_pil.size
	#print(img_sdfsdfpil.size)
	# Text 배경 이미지  ( 한글 두줄 까지 가능....)
	img_pil.paste(bgImg, (0, yLen-80))
	draw = ImageDraw.Draw(img_pil)
	# Text 쓰기
	draw.text((20, yLen - 72 ),  PText, font=font, fill=(b,g,r,a))

	# Opencv형식으로 변환하여 return
	frame = numpy.array(img_pil)
	return frame


def send_alert_mail(name,image_file):
	return requests.post(
		"https://api.mailgun.net/v3/sandboxd7906a8ebd724b33a1a81019f9fa8622.mailgun.org/messages",
		auth=("api", "5704c488f45c7a360300449df4d6ee97-ba042922-7dbcf980"),
		files = [("attachment", ("image.jpg", open(image_file, "rb").read()))],
		data={"from": "Mailgun Sandbox <postmaster@sandboxd7906a8ebd724b33a1a81019f9fa8622.mailgun.org>",
			"to": "Sangjun Shin <bluefinder@naver.com>",
			"subject": "발열자 정보입니다.",
			"html": "<html>" + name + " 의 온도가 높게 측정됩니다.<br>보건용 온도계로 다시 측정하시기 바랍니다.</html>"})

def send_alert_gmail(name, image_file):
	if name == "Unknown" or name == "unknown": return
	import smtplib
	from email.mime.text import MIMEText
	from email.mime.image import MIMEImage
	from email.mime.multipart import MIMEMultipart
	msg = MIMEMultipart()
	
	gmail_user = "op@twitchdarkbot.com"
	gmail_passwd = "Tlsehdbs080&"
	to = ["doyun.shin@gmail.com"]

	title = ""
	content = ""




	too = ""
	for i in range(len(to)): 
		if i == 0: too+="<"+str(i)+">"
		else: too+=", <"+str(i)+">"


	msg['From'] = gmail_user
	msg['To'] = too
	msg.attach(MIMEText(content))
	msg["Subject"] = title
	try:	
		server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
		server.eclo()
		server.login(gmail_user, gmail_passwd)
	except:
		print("Something went wrong")
	


# 학생증의 바코드 검출
def barcode_check(frame):
	try:
		barcodes = pyzbar.decode(frame)
		# 검출한 바코드(barcodes)를 위한 루프

		barcodeData = None

		for barcode in barcodes:
			# 바코드의 영역을 추출하고 영역 그리기
			# 이미지의 바코드 주변에 박스를 그림
			(x, y, w, h) = barcode.rect
			cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 0, 255), 2)
			# 바코드 데이터는 바이트 객체이므로 이미지에 그리려면 문자열을 먼져 바꿔야 한다.
			barcodeData = barcode.data.decode("utf-8")
			barcodeType = barcode.type
			# 바코드 데이터와 타입을 이미지에 그림
			text = "{} ({})".format(barcodeData, barcodeType)
			cv2.putText(frame, text, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX,
			0.5, (0, 0, 255), 2)	
			# 바코드타입과 데이터를 터미널에 출력
			print("[INFO] Found {} barcode: {}".format(barcodeType, barcodeData))
	except expression as identifier:
		pass	
	return frame, barcodeData


#전체 사진에서 얼굴 부위만 잘라 리턴
def face_extractor(img):
    #흑백처리 
    #img = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
    #얼굴 찾기 
    faces = face_classifier.detectMultiScale(img,1.3,5)
    #찾은 얼굴이 없으면 None으로 리턴 
    if faces is():
        return None
    #얼굴들이 있으면 
    for(x,y,w,h) in faces:
        #해당 얼굴 크기만큼 cropped_face에 잘라 넣기 
        #근데... 얼굴이 2개 이상 감지되면??
        #가장 마지막의 얼굴만 남을 듯
        cropped_face = img[y-30:y+h+30, x-20:x+w+20]
    #cropped_face 리턴 
    return cropped_face

# 신규 사용자 사진 찍기
def add_new_student(std_num,cap):
	time.sleep(1)
	#저장할 이미지 카운트 변수 
	count = 0
	# 사용자 폴더가 있는지 확인 및 생성
	if std_num == "S205095": std_num = "doyun"
	if std_num == "S205092": std_num = "taehyun"

	try:
		if not os.path.exists("dataset/"+std_num):
			os.makedirs("dataset/"+std_num)
	except OSError:
		print ('Error: Creating directory. ' +  directory)
		return False
	
	face = vs.read()
	#frame = cv2.resize(face_extractor(frame),(300,300))
	#frame1 = cv2.flip(frame, 1)
	#cv2.imshow('ADD_HEADSHOT',frame1)
	#time.sleep(1)

	while True:
		# 카메라로 부터 사진 1장 얻기 
		face = vs.read()
		face = cv2.flip(face, 1)		
		#얼굴 감지 하여 얼굴만 가져오기 
		if face_extractor(face) is not None:
			count+=1
			#얼굴 이미지 크기를 200x200으로 조정 
			#face = cv2.resize(face_extractor(frame1),(300,300))
			##face1 = face_extractor(face)
			face1 = face
			#조정된 이미지를 흑백으로 변환 
			#face = cv2.cvtColor(face, cv2.COLOR_BGR2GRAY)
			#faces폴더에 jpg파일로 저장 
			# ex > faces/user0.jpg   faces/user1.jpg ....

			file_name_path = 'dataset/'+std_num+'/'+std_num+'_'+str(count)+'.jpg'          
			cv2.imwrite(file_name_path,face1)
			
			#화면에 얼굴과 현재 저장 개수 표시          
			cv2.putText(face,str(count),(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
			cv2.imshow('ADD_HEADSHOT',face)
			#time.sleep(0.1)
		else:
			#print("Face not Found")
			#cv2.putText(frame,"Face not Found",(50,100),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
			cv2.putText(face,str(count) + "\nFace not Found",(50,50),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
			cv2.imshow('ADD_HEADSHOT',face)

		if cv2.waitKey(1)==ord("q") or count==30:
			break

	#cap.release()
	cv2.destroyWindow("ADD_HEADSHOT")
	print('Colleting Samples Complete!!!')
	return True

class jsonmanager(Exception):
	def __init__(self):
		from os.path import isfile
		if isfile("data.json"):
			pass
		else:
			f = open("data.json", "w")
			f.write("{}")
			f.close()
		pass

	def getdata(self):
		from json import load
		f = open("data.json", "r")
		try:
			rtn = load(f)
		except:
			print("Error while open json file.")
			print(f.read())
			rtn = {}
		
		return rtn

	def write(self, data):
		from json import dumps
		f = open("data.json", "w")
		f.write(dumps(data))
		f.close()

	def search(self, data):
		j = self.getdata()
		try:
			print(j[data])
		except:
			print("Cannot check the json")
		return j[data]



# 학습한 Data load
#Initialize 'currentname' to trigger only when a new person is identified.
currentname = "unknown"
#Determine faces from encodings.pickle file model created from train_model.py
encodingsP = "encodings.pickle"
#use this xml file
cascade = "haarcascade_frontalface_default.xml"

# load the known faces and embeddings along with OpenCV's Haar
# cascade for face detection
print("[INFO] loading encodings + face detector...")
data = pickle.loads(open(encodingsP, "rb").read())
detector = cv2.CascadeClassifier(cascade)

# MLX90614 온도 센서 세팅
bus = SMBus(1)
sensor = Adafruit_AMG88xx()
bsensor = MLX90614(bus, address=0x5A)

# 카메라 초기화 
print("[INFO] starting video stream...")
vs = VideoStream(src=0).start()
#vs = VideoStream(usePiCamera=True).start()
time.sleep(2.0)

# start the FPS counter
fps = FPS().start()

# 기타 설정 초기화
bgImg = Image.open('text_bg.jpg')
thermal_img = None
max_thermal = None
#얼굴검출 최소 넓이 (픽셀)
PASS_HSIZE = 220
rect_HSize = 0
rect_VSize = 0
barcode_data = None
sent_mail_name = ['Unknown']
jm = jsonmanager()

# loop over frames from the video file stream
while True:
	# 카메라에서 한 프레임 가져옴.
	frame = vs.read()
	frame = imutils.resize(frame, width=640, height=480)
	frame = cv2.flip(frame,1)
	# 8*8 이미지 센서 호출, 이미지와 최대 온도가져옴.
	# 시간차가 생김으로 카메라 프레임 가져오고 바로 가져온다.
	thermal_img ,max_thermal= thermal_draw(sensor)

	#학생증의 바코드 검출
	frame, barcode_data = barcode_check(frame)

	

	if barcode_data != None:
		# 학생증의 바코드 검출되었을때 처리.
		# Add student cam
		if not os.path.exists("dataset/"+str(barcode_data)):
			print(barcode_data)

			frame = write_hangul_text(frame, bgImg, "신규 사용자를 등록 합니다.\n카메라를 정면으로 바라보세요.")
			cv2.imshow("Recognition", frame)
			time.sleep(2)

			if add_new_student(str(barcode_data),vs):
				# 다시 기계학습 필요
				continue
			else:
				continue


		


	# convert the input frame from (1) BGR to grayscale (for face
	# detection) and (2) from BGR to RGB (for face recognition)
	# 얼굴 인식 과 처리 부분..
	gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

	# detect faces in the grayscale frame
	rects = detector.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30), flags=cv2.CASCADE_SCALE_IMAGE)

	# OpenCV returns bounding box coordinates in (x, y, w, h) order
	# but we need them in (top, right, bottom, left) order, so we
	# need to do a bit of reordering
	boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

	# compute the facial embeddings for each face bounding box
	encodings = face_recognition.face_encodings(rgb, boxes)
	names = []

	# loop over the facial embeddings
	for encoding in encodings:
		# attempt to match each face in the input image to our known
		# encodings
		matches = face_recognition.compare_faces(data["encodings"], encoding, tolerance=0.3)
		#print(matches)
		name = "Unknown" # 등록 안된 사람이라면.. Unknown처리

		# 등록된 사람이라면..
		if True in matches:
			# find the indexes of all matched faces then initialize a
			# dictionary to count the total number of times each face
			# was matched
			matchedIdxs = [i for (i, b) in enumerate(matches) if b]
			counts = {}

			# loop over the matched indexes and maintain a count for
			# each recognized face face
			for i in matchedIdxs:
				name = data["names"][i]
				counts[name] = counts.get(name, 0) + 1

			# determine the recognized face with the largest number
			# of votes (note: in the event of an unlikely tie Python
			# will select first entry in the dictionary)
			name = max(counts, key=counts.get)
			
			#If someone in your dataset is identified, print their name on the screen
			if currentname != name:
				currentname = name
				print(currentname)
		
		# update the list of names
		names.append(name)

	# 얼굴에 사각형및 이름 표시
	for ((top, right, bottom, left), name) in zip(boxes, names):
		rect_HSize = right - left
		rect_VSize = right - left
		# draw the predicted face name on the image - color is in BGR
		cv2.rectangle(frame, (left, top), (right, bottom),(0, 255, 225), 2)
		y = top - 15 if top - 15 > 15 else top + 15
		cv2.putText(frame, name, (left, y), cv2.FONT_HERSHEY_SIMPLEX, .8, (0, 255, 255), 2)
	
	
	# 8*8 온도센서의 이미지를 카메라 이미지위에 표시
	open_cv_image = cv2.cvtColor(numpy.array(thermal_img), cv2.COLOR_RGB2BGR)
	rows,cols,channels = open_cv_image.shape
	roi = frame[0:rows, 0:cols]
	img2gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
	ret,mask = cv2.threshold(img2gray,10,255,cv2.THRESH_BINARY)
	mask_inv = cv2.bitwise_not(mask)
	img_bg = cv2.bitwise_and(roi,roi,mask = mask_inv)
	img_fg = cv2.bitwise_and(open_cv_image,open_cv_image,mask = mask)
	dst = cv2.add(img_bg, img_fg)
	frame[0:rows,0:cols] = dst
	# 8*8 온도센서의 max 온도 표시
	cv2.putText(frame, str(max_thermal), (15, 120), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (0, 0, 255), 1)



	# 사람이 한명이면
	if len(names) == 1:
		try: od = bsensor.get_obj_temp()
		except expression as identifier: print("MLX90614 센서 에러!!")

		if names[0] == 'Unknown': frame = write_hangul_text(frame, bgImg, "미등록 인원입니다. 관리자를 통하여 등록하세요.\n측정온도 : {:.2f}".format(od+2))
		elif rect_HSize > PASS_HSIZE and max_thermal > 27:  # 온도센서가 27도 이상 되지 않으면 멀리 있거나 사진으로 하는것으로 판단
			# MLX90614 온도 측정
			# 예외 처리를 해야함..... 에러날수도..
			
			if od <= 36 and od>30: 
				frame = write_hangul_text(frame, bgImg, names[0] + "님. 체온측정이 완료. 정상!\n측정온도 : {:.2f}".format(od+2))
				#
				#  정상 측정된 사람에 대해 처리 로직 필요.
				#
				sFilename = names[0]+"_" +str(datetime.today().strftime('%Y%m%d%H%M%S'))
				file_name_path = 'photo/'+sFilename+'.jpg'          
				cv2.imwrite(file_name_path,frame)				
				#print("email send! : "+ file_name_path)
				#send_alert_mail(names[0], file_name_path)

				print(names[0] + "님. 측정온도 :  {:.2f}".format(od+2) + "   {} , {}", rect_HSize, rect_VSize )
				
			elif od>36: 
				# save image
				# 이메일보내기
				sFilename = names[0]+"_" +str(datetime.today().strftime('%Y%m%d%H%M%S'))
				file_name_path = 'photo/'+sFilename+'.jpg'          
				cv2.imwrite(file_name_path,frame)
				if names[0] == "Unknown" or name=="unknown": pass
				else:
					print("email send! : "+ file_name_path)
					send_alert_mail(names[0], file_name_path)

				frame = write_hangul_text(frame, bgImg, "인증온도계로 체온을 측정하세요.\n측정온도 : {:.2f}".format(od+2))
				# 추후 신규 등록 로직 수행
			else: 
				frame = write_hangul_text(frame, bgImg, "체온이 검출 되지 않습니다.\n\n측정온도 : {:.2f}".format(od+2))
		elif rect_HSize <= PASS_HSIZE :
			frame = write_hangul_text(frame, bgImg, "스크린 중앙에 얼굴이 위치하도록\n가까이 오시기 바랍니다.")
		else:
			frame = write_hangul_text(frame, bgImg, "온도 측정 범위를 벗어났습니다.\n\n측정온도 : {:.2f}".format(max_thermal))
	elif len(names) > 1:
		frame = write_hangul_text(frame, bgImg, "한명만 측정해 주시기 바랍니다.")

	# 최종 이미지 표시
	cv2.imshow("Recognition", frame)
	cv2.namedWindow("Recognition", cv2.WINDOW_NORMAL)
	cv2.setWindowProperty("Recognition", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

	# 변수초기화
	rect_HSize = 0
	rect_VSize = 0
	barcode_data=""

	key = cv2.waitKey(1) & 0xFF
	# quit when 'q' key is pressed
	if key == ord("q"):
		break

	# update the FPS counter
	fps.update()


# stop the timer and display FPS information
fps.stop()
print("[INFO] elasped time: {:.2f}".format(fps.elapsed()))
print("[INFO] approx. FPS: {:.2f}".format(fps.fps()))

# do a bit of cleanup
cv2.destroyAllWindows()
vs.stop()

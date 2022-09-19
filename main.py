import numpy as np #importing necessary libraries
import cv2
import face_recognition
import os
from datetime import datetime
import csv
import pandas as pd
import json
import requests

path = 'ImagesAttendace1'
images = []
classNames = []
myList = os.listdir(path)

print(myList) #to check the data availiable

for cl in myList: #getting the names from images
    curImg = cv2.imread(f'{path}/{cl}')
    images.append(curImg)
    classNames.append(os.path.splitext(cl)[0])
print(classNames)

def findEncodings(images): #encoding images
    encodelist = []
    for img in images:
        img = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodelist.append(encode)
    return encodelist

def markAttendacne(name): #marking attendance to csv file
    with open('Attendance.csv', 'r+') as f:
        myDataList = f.readlines()
        namelist = []
        for line in myDataList:
            entry = line.split(',')
            namelist.append(entry[0])
        if name not in namelist:
            now = datetime.now()
            dtString = now.strftime('%H:%M:%S')
            f.writelines(f'\n{name},{dtString}')

# markAttendacne('alibi')
encodeListKnown = findEncodings(images)
print("Encoding complete")

cap = cv2.VideoCapture(0)

file = open('Attendance.csv')
csvreader = csv.reader(file)
count = 0
while count<8: # 2 * count the number of workers/students needed to enter the job/classes
    for row in csvreader:
        count += 1
        print(row)

    success,img = cap.read()
    imgS = cv2.resize(img,(0,0),None,0.25,0.25)
    imgS = cv2.cvtColor(imgS,cv2.COLOR_BGR2RGB)

    facesCurrFrame = face_recognition.face_locations(imgS)
    encodesCurrFrame = face_recognition.face_encodings(imgS,facesCurrFrame)

    for encodeFace, faceloc in zip(encodesCurrFrame,facesCurrFrame):
        matches = face_recognition.compare_faces(encodeListKnown,encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown,encodeFace)
        # print(faceDis)
        matchIndex =np.argmin(faceDis)
        if matches[matchIndex]:
            name = classNames[matchIndex].upper()
            y1,x2,y2,x1 = faceloc
            y1, x2, y2, x1 = y1*4,x2*4,y2*4,x1*4
            cv2.rectangle(img, (x1,y1),(x2,y2),(0,255,0),2)
            cv2.rectangle(img,(x1,y2-35),(x2,y2),(0,255,0),cv2.FILLED)
            cv2.putText(img,name,(x1+6,y2-6),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),2)
            markAttendacne(name)
        else:
            name = "None"
            y1, x2, y2, x1 = faceloc
            y1, x2, y2, x1 = y1 * 4, x2 * 4, y2 * 4, x1 * 4
            cv2.rectangle(img, (x1, y1), (x2, y2), (0,0,255), 2)
            cv2.rectangle(img, (x1, y2 - 35), (x2, y2), (0,0,255), cv2.FILLED)
            cv2.putText(img, name, (x1 + 6, y2 - 6), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 255, 255), 2)
        # print(faceDis)
    cv2.imshow('Webcam',img)
    cv2.waitKey(1)


df = pd.read_csv('Attendance.csv') #converting csv to excel to upload it to google drive
df.to_excel('Attendance.xlsx', index=None, header=True)
headers = {"Authorization": "Bearer ya29.a0Aa4xrXOE9tRKS_KVXZcvjKXnkhJ_e4KE7BpUjpoTkdohqPy4D3Lyqclv6BJ6ntU8ZR-jioxTQBVMebJSjZILkvQQZaVLVtumzCoTFlL1wdJ6GZcU1HvLGmOthGzJiLXOXSHGyD8_xoaTRHe1siAqtN97U7jdaCgYKATASARISFQEjDvL9q9wiIuGarO25CrAs1Jliig0163"}
#the code after Bearer can be changed if you get code for an API
para = {
    "name": 'Attendance.xlsx',
}
files = {
    'data': ('metadata', json.dumps(para), 'application/json; charset=UTF-8'),
    'file': open("./Attendance.xlsx", "rb")
}
r = requests.post(
    "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart",
    headers=headers,
    files=files
)
print("Process has finished")

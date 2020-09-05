from pymongo import MongoClient
import numpy as np
import cv2
import re
import time
import os
import base64
cv2.ocl.setUseOpenCL(False)
client = MongoClient('localhost', 27017)
db = client.userDatabase
collection = db.userData
captureImage = False

def rollIsCorrect(rollNo):
    matchObj = re.match(r'[0-9][0-9]-[0-9]-[0-9]-[0-9][0-9][0-9]',rollNo,re.I)
    if matchObj:
        return True
    return False

def alreadyExist(rollNo):
    cursor = db.userData.find({"roll_no": rollNo})
    if cursor.count() != 0:
        return True
    return False

def addData():
    name = raw_input("Enter Your Name : ")
    while True:
        rollNo = raw_input("Enter Your Roll Number : ")
        if rollIsCorrect(rollNo):
            break
        else:
            print "Roll No. is not in correct format! Please Enter again."
    if alreadyExist(rollNo):
        print "User with this roll number already exists!"
    else:
        startScan = raw_input("Place your hand on the scanner and press 1 : ")
        if startScan == "1":
            print "Capturing Image! do not remove your hand!"
            cap = cv2.VideoCapture(0)
            ret, image = cap.read()
            cv2.imwrite("tatti.jpg",image)
            image = cv2.imread("tatti.jpg",0)
            os.remove("tatti.jpg")
            print "Image Captured! You can now remove your hand!"
            orb = cv2.ORB_create(nfeatures = 200)
            blur = cv2.GaussianBlur(image,(5,5),0)
            ret,th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            cv2.imwrite("tatti1.jpg",th)
            key_points, des_main = orb.detectAndCompute(th, None)
            td = [[1,2,3,4,5]]
            for i in des_main:
                td.append(i.tolist())
            td.append([6,7,8,9])
            post = {
                "user_name": name,
                "roll_no": rollNo,
                "td":td,
            }
            collection.insert_one(post)
            cap.release()
            cv2.destroyAllWindows()
            print "User Successfully Added!!"
        else:
            print "Wrong input! Start Again.."
    
def deleteData():
    name = raw_input("Enter Your Name : ")
    while True:
        rollNo = raw_input("Enter Your Roll Number : ")
        if rollIsCorrect(rollNo):
            break
        else:
            print "Roll No. is not in correct format! Please Enter again."
    if alreadyExist(rollNo):
        db.userData.delete_one({"roll_no":rollNo})
        print "User Deleted Successfully!"
    else:
        print "User Does not Exists!"

def login():
    name = raw_input("Enter Your Name : ")
    while True:
        rollNo = raw_input("Enter Your Roll Number : ")
        if rollIsCorrect(rollNo):
            break
        else:
            print "Roll No. is not in correct format! Please Enter again."
    if alreadyExist(rollNo):
        startScan = raw_input("Place your hand on the scanner and press 1 : ")
        if startScan == "1":
            print "Capturing Image! do not remove your hand!"
            cap = cv2.VideoCapture(0)
            ret, image = cap.read()
            cv2.imwrite("tatti.jpg",image)
            image = cv2.imread("tatti.jpg",0)
            os.remove("tatti.jpg")
            print "Image Captured! You can now remove your hand!"
            cursor = db.userData.find({"roll_no": rollNo})
            td=[]
            for results in cursor:
                td = results["td"]
            td = td[1:len(td)-1]
            print len(td)
            des_main = np.array(td,dtype=np.uint8)
            orb = cv2.ORB_create(nfeatures= 200)
            blur = cv2.GaussianBlur(image,(5,5),0)
            ret,th = cv2.threshold(blur,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            key_points, des_query = orb.detectAndCompute(th, None)
            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=False)
            matches = bf.knnMatch(des_main, des_query, k=2)
            print len(matches)
            good = []
            for m, n in matches:
                if m.distance < 0.9 * n.distance:
                    good.append([m])
            print len(good)
            if len(good) > 120: 
                print "Login Successful!!"
            else:
                print "Login Failed!!"
            cap.release()
            cv2.destroyAllWindows()
        else:
            print "Wrong Input!Start Afresh.."
    else:
        print "User Does not Exists!"
while True:
    print "Palm Vein Pattern Authentication System"
    flag = raw_input("1) Enter 1 for adding new record\n2) Enter 2 for Logging in\n3) Enter 3 for deleting existing record\n4) Enter 4 for exiting\nYour input : ")
    if flag not in ["1","2","3","4"]:
        print "Wrong Input!!"
    elif flag == "1":
        addData()
    elif flag == "2":
        login()
    elif flag == "3":
        delete()
    elif flag == "4":
        break

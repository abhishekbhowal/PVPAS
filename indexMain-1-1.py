import Tkinter as tk
import tkMessageBox
from pymongo import MongoClient
import numpy as np
from PIL import Image,ImageTk
import multiprocessing
import cv2
import re
import time
import os
import thread
from matplotlib import pyplot as plt
import base64
cv2.ocl.setUseOpenCL(False)
stopVideo = False
client = MongoClient('localhost', 27017)
db = client.userDatabase
collection = db.userData
captureImage = False

def rollIsCorrect(rollVar):
    matchObj = re.match(r'[0-9][0-9]-[0-9]-[0-9]-[0-9][0-9][0-9]',rollVar,re.I)
    if matchObj:
        return True
    return False

def addData(nameVar,rollVar):
    if not rollIsCorrect(rollVar):
        tkMessageBox.showinfo("Invalid Data Format", "Data format is wrong!")
    else:
        if alreadyExist(rollVar):
            tkMessageBox.showinfo("Redundant Data", "User Already Exists..")
        elif nameVar is "" or rollVar is "":
            tkMessageBox.showinfo("Form Incomplete", "Please Fill All The Credentials!")
        else: 
            global captureImage
            captureImage = True
            if not os.path.isfile("test.jpg"):
                time.sleep(5)
            img = cv2.imread('test.jpg')
            string =cv2.imencode(".jpg",img)[1]
            b64 = base64.b64encode(string)
            post = {
                "userName" : nameVar.upper(),
                "rollNo" : rollVar.upper(),
                "image" : b64
            }
            db.userData.insert_one(post)
            tkMessageBox.showinfo("Success", "New User Added!")
            os.remove("test.jpg")

def alreadyExist(rollVar):
    cursor = db.userData.find({"rollNo": rollVar})
    if cursor.count() != 0:
        return True
    return False

def deleteData(nameVar, rollVar):
    if not rollIsCorrect(rollVar):
        tkMessageBox.showinfo("Invalid Data Format", "Data format is wrong!")
    else:
        if not alreadyExist(rollVar):
            tkMessageBox.showinfo("Record Not Found", "User Does Not Exists..")
        else:
            db.userData.delete_one({"rollNo":rollVar})
            tkMessageBox.showinfo("Deleted!", "The User is Deleted")

def login(nameVar, rollVar):
    if not rollIsCorrect(rollVar):
        tkMessageBox.showinfo("Invalid Data Format", "Data format is wrong!")
    else:
        global captureImage
        if alreadyExist(rollVar):
            cursor = db.userData.find({"rollNo": rollVar})
            for results in cursor:
                img_str = results["image"]

            captureImage = True
            orb = cv2.ORB_create(nfeatures = 100)
            if not os.path.isfile("test.jpg"):
                time.sleep(5)
            img2 = cv2.imread("test.jpg",0)
            blur2 = cv2.GaussianBlur(img2,(5,5),0)
            ret2,th2 = cv2.threshold(blur2,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            kp, des_query = orb.detectAndCompute(th2,None)
            print len(des_query)
            
            string = base64.b64decode(img_str)
            nparray=np.fromstring(string,np.uint8)
            img1 = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
            cv2.imwrite("test.jpg",img1)
            img1 = cv2.imread("test.jpg",0)
            os.remove("test.jpg")
            
            blur1 = cv2.GaussianBlur(img1,(5,5),0)
            ret1,th1 = cv2.threshold(blur1,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
            key_points, des_main = orb.detectAndCompute(th1, None)
            print len(des_main)

            bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
            matches = bf.knnMatch(des_main, des_query, k = 2)
            print len(matches)
            
            good = []
            
            for m, n in matches:
                if m.distance < 0.9 * n.distance:
                    good.append([m])
            print len(good)
            
            if len(good) > 180:    
                text = "Hello " + nameVar + ", Roll No. " + rollVar 
                tkMessageBox.showinfo("Welcome!", text)
            else:
                tkMessageBox.showinfo("Login Failed", "Invalid Credentials")
            os.remove("test.jpg")
        else:
            tkMessageBox.showinfo("Login Failed", "Record Not Found!")
        
        
def captureVideo():
    global captureImage
    cap = cv2.VideoCapture(0)
    while not stopVideo:
        ret, imFrame = cap.read()
        if captureImage:
            captureImage = False
            cv2.imwrite("test.jpg",imFrame)
        if ret is True:
            image = cv2.cvtColor(imFrame,cv2.COLOR_BGR2RGB)
            image = Image.fromarray(image)
            image = ImageTk.PhotoImage(image)
            ret = cap.set(3,640)
            ret = cap.set(4,480)
            panel.configure(image = image)
            panel.image = image
            panel.update()
    if stopVideo:
        cap.release()

def makeWindow():
    window = tk.Tk()
    window.wm_title("PVPAS - Data Entry")
    window.minsize(320,240)
    window.maxsize(640,480)

    #Text Input Frame
    frame1 = tk.Frame(window)
    frame1.pack()
    tk.Label(frame1, text="Name").grid(row=0,column=0,sticky="W")
    name = tk.Entry(frame1)
    name.grid(row=0, column=1, sticky="W")
    tk.Label(frame1, text="Roll No").grid(row=1, column=0, sticky="W")
    roll = tk.Entry(frame1)
    roll.grid(row=1, column=1, sticky="W")

    frame3 = tk.Frame(window)
    frame3.pack()
    add = tk.Button(frame3,text="Add",command=lambda: addData(name.get(),roll.get()))
    verify = tk.Button(frame3,text="Login",command=lambda: login(name.get(), roll.get()))
    #update = tk.Button(frame3,text="Update",command=lambda: updateData(name.get(),roll.get()))
    delete = tk.Button(frame3,text="Delete",command=lambda: deleteData(name.get(), roll.get()))
    add.pack(side="left")
    verify.pack(side="left")
    #update.pack(side="left")
    delete.pack(side="left")

    #Video Feed Frame
    global frame2,panel
    img = ImageTk.PhotoImage(Image.open("video_feed_dummy_image.jpg", mode="r"))
    frame2 = tk.Frame(window)
    frame2.pack()
    panel = tk.Label(frame2,image=img)
    panel.image = img
    panel.pack(side="left",padx=10,pady=10)
    
if __name__ == '__main__':
    win = makeWindow()
    captureVideo()
    tk.mainloop()
    












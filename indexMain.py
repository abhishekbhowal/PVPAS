import Tkinter as tk
import tkMessageBox
import threading
#from pymongo import MongoClient
import numpy as np
from PIL import Image,ImageTk
import multiprocessing
import cv2
cv2.ocl.setUseOpenCL(False)
stopVideo = False
#client = MongoClient('localhost', 27017)
#db = client.mydb
#collection = db.user_database
captureImage = False

def addData(nameVar,rollVar):
    
    if(alreadyExist(rollVar, nameVar)):
        #tkMessageBox.showinfo("Redundant Data", "User Already Exists..")
        pass
    
    else:
        global captureImage
        captureImage = True
        img = cv2.imread('test.jpg',0)
        orb = cv2.ORB_create()
        key_points, desc = orb.detectAndCompute(img, None)
        td = []
        for i in desc:
            td.append(i.tolist())
        #print td

        post = {
            "userName" : nameVar.upper(),
            "rollNo" : rollVar.upper(),
            "training_descriptors" : td
        }
        #db.user_database.insert_one(post)
        tkMessageBox.showinfo("Success", "Data Added..")


def alreadyExist(rollVar,nameVar):
    pass
    #cursor = db.user_database.find({"rollNo": rollVar})
    #if cursor:
     #   return True
    #return False

def deleteData(nameVar, rollVar):
    if not alreadyExist(rollVar,nameVar):
        #tkMessageBox.showinfo("Record Not Found", "User Does Not Exists..")
        pass
    else:
        #db.user_database.delete_one({"rollNo":rollNo})
        pass
    pass

def updateData():
    pass

def login(nameVar, rollVar):
    if alreadyExist(rollVar,nameVar):
        pass
    else:
        #tkMessageBox.showinfo("Record Not Found", "Login Failed!")
        pass
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
            ret = cap.set(3,320)
            ret = cap.set(4,240)
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
    update = tk.Button(frame3,text="Update",command=lambda: updateData(name.get(),roll.get()))
    delete = tk.Button(frame3,text="Delete",command=lambda: deleteData(name.get(), roll.get()))
    add.pack(side="left")
    verify.pack(side="left")
    update.pack(side="left")
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












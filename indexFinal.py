import Tkinter as tk
import tkMessageBox
import multiprocessing
from pymongo import MongoClient
import numpy as np
from PIL import Image,ImageTk
import cv2
import re
import time
import base64
import Queue
#from picamera.array import PiRGBArray
#from picamera import PiCamera

cv2.ocl.setUseOpenCL(False) #OpenCV error resolution
client = MongoClient('localhost', 27017) #database ip and port 
db = client.userDatabase # DB Name = userDatabase, referencing it here
collection = db.userData # Collection Name = userData, referencing it here
#cap = cv2.VideoCapture(0)
#Helper Function 1
#checks the formatting of roll number

def img_capture(queue):
    cap = cv2.VideoCapture()
    while True:
        flag, frame= cap.read()
        #frame = cv2.cvtColor(frame,cv2.cv.CV_BGR2RGB)
        queue.put(frame)

def rollIsCorrect(rollVar):
    matchObj = re.match(r'[0-9][0-9]-[0-9]-[0-9]-[0-9][0-9][0-9]',rollVar,re.I)
    if matchObj:
        return True
    return False

#Helper Function 2
#checks if user exists or not
def alreadyExist(nameVar, rollVar):
    cursor = db.userData.find({"rollNo": rollVar})
    if cursor.count() != 0:
        return True
    return False

#Main Function 1
#Used to add data to database
def addData(nameVar, rollVar,task):
    if nameVar is "" or rollVar is "":
        tkMessageBox.showwarning("Form Is Incomplete", "Please Complete The Form!!")
    elif not rollIsCorrect(rollVar):
        tkMessageBox.showerror("Wrong Data Format", "Roll Number is in wrong Format")
    elif alreadyExist(nameVar, rollVar):
        tkMessageBox.showerror("Redundant Entry", "User Already Exists!")
    else:
        global frame3, panel,img_back1
        #camera = PiCamera()
        #camera.resolution = (640, 480)
        #camera.framerate = 32
        #rawCapture = PiRGBArray(camera, size=(640, 480))
        #time.sleep(1)
        #camera.capture(rawCapture, format="bgr")
        #image = rawCapture.array
        #image_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        #image_rgb = ImageTk.PhotoImage(image_rgb)
        #panel.configure(image = image_rgb)
        #panel.image = image_rgb
        #time.sleep(3)
        #ret, image = cap.read()
        #queue.put(image)
        p = multiprocessing.Process(target=img_capture, args=(task,))
        p.start()
        image = task.get()
        image_rgb = cv2.cvtColor(image,cv2.COLOR_BGR2RGB)
        image_rgb = Image.fromarray(image_rgb)
        image_rgb = ImageTk.PhotoImage(image_rgb)
        ret = cap.set(3,640)
        ret = cap.set(4,480)
        panel.configure(image = image_rgb)
        panel.image = image_rgb
        panel.update()
        panel.after(5,lambda:addData(nameVar,rollVar,task))
        if tkMessageBox.askyesno("Data Entry","Confirm Submission?"):
            string = cv2.imencode(".jpg",image)[1]
            b64 = base64.b64encode(string)
            post = {
                "userName" : nameVar.upper(),
                "rollNo" : rollVar.upper(),
                "image" : b64
            }
            db.userData.insert_one(post)
            tkMessageBox.showinfo("Success", "New User Added!")
        p.terminate()
def login(nameVar, rollVar):
    if nameVar is "" or rollVar is "":
        tkMessageBox.showwarning("Form Is Incomplete", "Please Complete The Form!!")
    elif not rollIsCorrect(rollVar):
        tkMessageBox.showerror("Wrong Data Format", "Roll Number is in wrong Format")
    elif alreadyExist(nameVar, rollVar):
        cursor = db.userData.find({"rollNo": rollVar})
        for results in cursor:
            img_str = results["image"]
        #image_rgb = ImageTk.PhotoImage(Image.open("dummy_image1.jpg", mode="r"))
        #image_rgb = ImageTk.PhotoImage(image_rgb)
        #panel.configure(image = image_rgb)
        #panel.image = image_rgb
        string = base64.b64decode(img_str)
        nparray=np.fromstring(string,np.uint8)
        img_main = cv2.imdecode(nparray,cv2.IMREAD_COLOR)
        cv2.imwrite("img_main.jpg",img_main)
        img_main = cv2.imread("img_main.jpg",0)
        orb = cv2.ORB_create(nfeatures = 100)
        ret, image_query = cap.read()
        blur_main = cv2.GaussianBlur(img_main,(5,5),0)
        ret_main,th_main = cv2.threshold(blur_main,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kp_main, des_main = orb.detectAndCompute(th_main,None)
        blur_query = cv2.GaussianBlur(img_query,(5,5),0)
        ret_query,th_query = cv2.threshold(blur_query,0,255,cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        kp_query, des_query = orb.detectAndCompute(th_query,None)
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck = False)
        matches = bf.knnMatch(des_main, des_query, k = 2)
        good = []
        for m, n in matches:
            if m.distance < 0.9 * n.distance:
                good.append([m])
        if len(good) > 60:
            tkMessageBox.showinfo("Login Result","Login Successful!!")
        elif len(good) > 40 and len(good) < 60:
            tkMessageBox.showwarning("Login Result", "Place your hand correctly!!")
        else:
            tkMessageBox.showerror("Login Result","Error Logging In..")
        
        
def deleteData(nameVar, rollVar):
    if nameVar is "" or rollVar is "":
        tkMessageBox.showwarning("Form Is Incomplete", "Please Complete The Form!!")
    elif not rollIsCorrect(rollVar):
        tkMessageBox.showerror("Wrong Data Format", "Roll Number is in wrong Format")
    elif alreadyExist(nameVar, rollVar):
        if tkMessageBox.askyesno("Confirm Operation","Are you sure?"):
            db.userData.delete_one({"rollNo":rollVar})
            tkMessageBox.showinfo("Deleted!", "The User is Deleted")
    else:
        tkMessageBox.showerror("Error","User does not exists!")

def makeWindow():
    #Defining the tkinter window
    task = multiprocessing.Queue()
    window = tk.Tk()
    window.wm_title("Palm Vein Pattern Auth System")
    window.minsize(640,540)
    window.maxsize(640,540)
    
    #Title Frame
    frame0 = tk.Frame(window)
    frame0.pack()
    tk.Label(frame0, text="Welcome!",font=("Arial", 40)).grid(row=0,column=0,sticky="W")
    
    #Frame-1
    #Takes user details as input
    frame1 = tk.Frame(window)
    frame1.pack(pady = 10)
    tk.Label(frame1, text="Name : ",font=("Arial", 12)).grid(row=0,column=0,sticky="W")
    nameVar = tk.Entry(frame1,font=("Arial", 12) )
    nameVar.grid(row=0, column=1, sticky="W")
    tk.Label(frame1, text="Roll No. : ",font=("Arial", 12)).grid(row=1,column=0,sticky="W")
    rollVar = tk.Entry(frame1,font=("Arial", 12))
    rollVar.grid(row=1, column=1, sticky="W")

    #Frame-2
    #Confirms Inputs
    frame2 = tk.Frame(window)
    frame2.pack(pady = 5)
    add_user = tk.Button(frame2, text="Add", font=("Arial", 12), command=lambda: addData(nameVar.get(),rollVar.get(),task))
    login_user = tk.Button(frame2, text="Login", font=("Arial", 12), command=lambda: login(nameVar.get(), rollVar.get()))
    delete_user = tk.Button(frame2,text="Delete", font=("Arial", 12),command=lambda: deleteData(nameVar.get(), rollVar.get()))
    add_user.pack(side="left", padx = 5)
    login_user.pack(side="left", padx = 5)
    delete_user.pack(side="left", padx = 5)
    
    #Frame-3
    #Image I/O
    global frame3, panel,img_back1
    frame3 = tk.Frame(window)
    frame3.pack(pady = 5, padx = 5)
    img_back1 = ImageTk.PhotoImage(Image.open("dummy_image1.jpg", mode="r"))
    panel = tk.Label(frame3,image=img_back1)
    panel.image = img_back1
    panel.pack(side="left",padx=10,pady=10)
    
if __name__ == '__main__':
    win = makeWindow()
    tk.mainloop()
    
    

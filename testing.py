import multiprocessing
import cv2
from PIL import Image,ImageTk
import Tkinter as tk

def image_capture(queue):
    vidFile = cv2.VideoCapture(0)
    while True:
        flag, frame=vidFile.read()
        frame = cv2.cvtColor(frame,cv2.COLOR_BGR2RGB)
        queue.put(frame)
        cv2.waitKey(10)

def update_all(root, imagelabel, queue, process, var):
    if var.get()==True:
        global im
        im = queue.get()
        a = Image.fromarray(im)
        b = ImageTk.PhotoImage(image=a)
        imagelabel.configure(image=b)
        imagelabel._image_cache = b
        root.update()
        root.after(0, func=lambda: update_all(root, imagelabel, queue, process, var))
    else:
        print var.get()
        root.quit()

def playvideo(root, imagelabel, queue, var):

    global im
    p = multiprocessing.Process(target=image_capture, args=(task,))
    p.start()
    update_all(root, imagelabel, queue, p, var)
    root.mainloop()
    p.terminate()
    if var.get()==False:
        try:
            cv2.imwrite("capturedFrame.jpg",im[:, :, ::-1])
            a = Image.fromarray(im)
            imagelabel.configure(image=a)
            imagelabel._image_cache = im
        except Exception,e:
            print e
    var.set(True)
    print 'finishing'

if __name__ == '__main__':
    try:
        task = multiprocessing.Queue()
        root = tk.Tk()
        image_label = tk.Label(master=root)
        image_label.grid(column=0, row=0, columnspan=2, rowspan=1)
        background = ImageTk.PhotoImage(file='img.jpg')
        image_label['image'] = background
        button_frame = tk.Frame(root)
        button_frame.grid(column=0, row=1, columnspan=1)

        load_button = tk.Button(master=button_frame, text='Load video',command=lambda: playvideo(root, image_label, task, switch))
        load_button.grid(column=0, row=0, sticky='ew')

        #Click button
        switch = tk.BooleanVar(master=root, value=True, name='switch')
        stop_button = tk.Button(master=button_frame, text='Click',command=lambda: switch.set(False))
        stop_button.grid(column=0, row=1, sticky='ew')

        #quit button
        quit_button = tk.Button(master=button_frame, text='Quit',command=root.destroy)
        quit_button.grid(column=0, row=2, sticky='ew')
        root.mainloop()

    except Exception,e:
        print e

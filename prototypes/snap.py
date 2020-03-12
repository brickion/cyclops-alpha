import tkinter as tk
import cv2
from PIL import Image, ImageTk
from tkinter import simpledialog
import face_recognition
import config, time

def show_frame():
    global frame
    _, frame = cap.read()
    frame = cv2.flip(frame, 1)
    cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    img = Image.fromarray(cv2image)
    imgtk = ImageTk.PhotoImage(image=img)
    lmain.imgtk = imgtk
    lmain.configure(image=imgtk)
    lmain.after(10, show_frame)
    #show_frame()

def capture_photo():
    person_name = simpledialog.askstring("Name", "Who is this person?", parent=root)
    global photo_counter
    photo_counter += 1
    photo_name = './faces/' + person_name + '_' + str(int(time.time())) + '.jpg'
    cv2.imwrite(filename=photo_name, img=frame)
    # cap.release()
    instruction_label['text']='Photo Captured!'

    img_new = cv2.imread(photo_name, cv2.IMREAD_GRAYSCALE)
    img_new = cv2.imshow("Captured Image", img_new)
    cv2.waitKey(1000)
    cv2.destroyAllWindows()
    # photo_counter = photo_counter+1
    instruction_label['text']='Photo Captured!\nRecognising Photo...'
    new_face = face_recognition.load_image_file(photo_name)
    instruction_label['text']='Photo Captured!\nPhoto Recognised!'
    new_face_encoding = face_recognition.face_encodings(new_face)[0]
    config.saveFace(person_name, new_face_encoding)
    instruction_label['text']=str(photo_counter) + ' Photo(s) Captured!\nPhoto Recognised!\nFace Stored!'

root = tk.Tk()
root.bind('<Escape>', lambda e: root.quit())

photo_counter = 0
lmain = tk.Label(root)
instruction_label = tk.Label(root, text='Click Capture to Take Photo')
cap = cv2.VideoCapture(0)
width, height = 800, 600
cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

lmain.pack()
instruction_label.pack()
capture_button = tk.Button(root, text='Capture', width=25, height=10, command=capture_photo)
capture_button.pack()
show_frame()
root.mainloop()

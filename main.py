import config
import json
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import snap, face_recognition, cv2, numpy as np

window = tk.Tk()
faces = []
names = []
video_capture = cv2.VideoCapture(0)

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

def capture_name():
    #person_name = simpledialog.askstring("Name", "Who is this person?", parent=window)
    #print(person_name)
    #print('hi')
    # status_label['text'] = 'launching...'
    status_label.after(200, snap.start())

def load_data():
    names, faces = config.loadJson()
    print(str(len(names)) + ' items loaded')
    print('names loaded')
    print(names)
    print('faces loaded')
    print(faces)

def render_main():
    load_data()

    window.title('Cyclops')

    title = tk.Label(text='Cyclops Optical', width=50, height=10)
    title.pack()

    separator = tk.Frame(height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(padx=5, pady=5)

    frame = tk.Frame(window)
    global capture_button
    capture_button = tk.Button(frame, text='New Person', width=25, height=10, command=capture_name)
    detect_button = tk.Button(frame, text='Detect', width=25, height=10, command=detect)
    capture_button.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
    detect_button.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
    frame.pack()

    bottom_frame = tk.Frame(window)
    bottom_frame.pack()

    global status_label
    status_label = tk.Label(bottom_frame, text='hello', width=50)
    status_label.pack(side = tk.BOTTOM, padx=5, pady=5, fill=tk.BOTH, expand=True)

    window.mainloop()

render_main()

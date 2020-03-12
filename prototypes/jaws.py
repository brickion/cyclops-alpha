import config
import json
import tkinter as tk
from tkinter import simpledialog
from PIL import Image, ImageTk
import snap, face_recognition, cv2, numpy as np

version = 0.1
width, height = 800, 600
window = tk.Tk()
cap = cv2.VideoCapture(0)
video_panel = tk.Label(window)

# def show_frame():
    # _, frame = cap.read()
    # frame = cv2.flip(frame, 1)
    # cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
    # img = Image.fromarray(cv2image)
    # imgtk = ImageTk.PhotoImage(image=img)
    # video_panel.imgtk = imgtk
    # video_panel.configure(image=imgtk)
    # video_panel.after(5, show_frame)
roy_image = face_recognition.load_image_file("./faces/obama.jpg")
roy_face_encoding = face_recognition.face_encodings(roy_image)[0]
known_face_encodings = [
    roy_face_encoding,
]
known_face_names = [
    "Roy Hui",
]

face_locations = []
face_encodings = []
face_names = []

def detect():
    # Initialize some variables

    ret, vid_frame = cap.read()
    small_frame = cv2.resize(vid_frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]

    face_locations = face_recognition.face_locations(rgb_small_frame)
    face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
        matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        name = "Unknown"
        face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        best_match_index = np.argmin(face_distances)
        if matches[best_match_index]:
            name = known_face_names[best_match_index]

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4
        cv2.rectangle(vid_frame, (left, top), (right, bottom), (0, 0, 255), 2)
        cv2.rectangle(vid_frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(vid_frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    cv2.imshow('Video', vid_frame)
    detect()
    # vid_frame = cv2.flip(vid_frame, 1)
    # cv2image = cv2.cvtColor(vid_frame, cv2.COLOR_BGR2RGBA)
    # img = Image.fromarray(cv2image)
    # imgtk = ImageTk.PhotoImage(image=img)
    # video_panel.imgtk = imgtk
    # video_panel.configure(image=imgtk)
    # video_panel.after(10, detect)


def main():
    window.title('Cyclops')
    window.bind('<Escape>', lambda e: window.quit())

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    title = tk.Label(text='Cyclops Optical', width=50, height=10)
    title.pack()
    video_panel.pack()

    separator = tk.Frame(height=2, bd=1, relief=tk.SUNKEN)
    separator.pack(padx=5, pady=5)

    button_frame = tk.Frame(window)

    capture_button = tk.Button(button_frame, text='New Person', width=25, height=10)
    detect_button = tk.Button(button_frame, text='Detect', width=25, height=10, command=detect)
    capture_button.pack(fill=tk.BOTH, side=tk.LEFT, expand=True)
    detect_button.pack(fill=tk.BOTH, side=tk.RIGHT, expand=True)
    button_frame.pack()

    bottom_frame = tk.Frame(window)
    bottom_frame.pack()

    status_label = tk.Label(bottom_frame, text='Welcome to cyclops V' + str(version), width=50)
    status_label.pack(side = tk.BOTTOM, padx=5, pady=5, fill=tk.BOTH, expand=True)

    window.mainloop()

main()

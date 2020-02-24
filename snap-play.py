import tkinter as tk
import cv2
from PIL import Image, ImageTk

class Snap(tk.Frame):
    def __init__(self):

        self.root = tk.Toplevel()
        self.root.geometry("900x700")

        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

        tk.Frame.__init__(self, self.root)
        self.create_widgets()
        self.show_frame()

        # root.bind('<Escape>', lambda e: root.quit())
        # root.bind('<Return>', enter_key)

    def create_widgets(self):
        # self.root.bind('<Return>', self.parse)
        # self.grid()
        # self.submit = tk.Button(self, text="Submit")
        # self.submit.bind('<Button-1>', self.parse)
        # self.submit.grid()

        self.lmain = tk.Label(self.root)
        self.lmain.pack()
        self.capture_button = tk.Button(text='Capture', width=25, height=10, command=self.capture_image)
        self.capture_button.pack()

    def show_frame(self):
        _, self.frame = self.cap.read()
        self.frame = cv2.flip(self.frame, 1)
        self.cv2image = cv2.cvtColor(self.frame, cv2.COLOR_BGR2RGBA)
        self.img = Image.fromarray(self.cv2image)
        self.imgtk = ImageTk.PhotoImage(image=self.img)
        self.lmain.imgtk = self.imgtk
        self.lmain.configure(image=self.imgtk)
        self.lmain.after(10, self.show_frame)

    def capture_image(self):
        cv2.imwrite(filename='saved_img.jpg', img=self.frame)

    # def start(self):
    #     self.root.mainloop()


# Application().start()



#
#
# def show_frame():
#     _, frame = cap.read()
#     frame = cv2.flip(frame, 1)
#     cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
#     img = Image.fromarray(cv2image)
#     imgtk = ImageTk.PhotoImage(image=img)
#     lmain.imgtk = imgtk
#     lmain.configure(image=imgtk)
#     lmain.after(10, show_frame)
#
# def enter_key(event):
#     capture_image()
#
# def capture_image():
#     print('hi')
#
#


#
# show_frame()
# root.mainloop()

# -------------
#
# def capture(person_name):
#     key = cv2. waitKey(1)
#     webcam = cv2.VideoCapture(0)
#     while True:
#         try:
#             check, frame = webcam.read()
#             #print(check) #prints true as long as the webcam is running
#             #print(frame) #prints matrix values of each framecd
#             cv2.imshow("Capturing", frame)
#             key = cv2.waitKey(1)
#             if key == ord('s'):
#                 cv2.imwrite(filename='saved_img.jpg', img=frame)
#                 webcam.release()
#                 img_new = cv2.imread('saved_img.jpg', cv2.IMREAD_GRAYSCALE)
#                 img_new = cv2.imshow("Captured Image", img_new)
#                 cv2.waitKey(1650)
#                 cv2.destroyAllWindows()
#                 print("Processing image...")
#                 img_ = cv2.imread('saved_img.jpg', cv2.IMREAD_ANYCOLOR)
#                 print("Converting RGB image to grayscale...")
#                 gray = cv2.cvtColor(img_, cv2.COLOR_BGR2GRAY)
#                 print("Converted RGB image to grayscale...")
#                 print("Resizing image to 28x28 scale...")
#                 img_ = cv2.resize(gray,(28,28))
#                 print("Resized...")
#                 img_resized = cv2.imwrite(filename='saved_img-final.jpg', img=img_)
#                 print("Image saved!")
#
#                 break
#             elif key == ord('q'):
#                 print("Turning off camera.")
#                 webcam.release()
#                 print("Camera off.")
#                 print("Program ended.")
#                 cv2.destroyAllWindows()
#                 break
#
#         except(KeyboardInterrupt):
#             print("Turning off camera.")
#             webcam.release()
#             print("Camera off.")
#             print("Program ended.")
#             cv2.destroyAllWindows()
#             break

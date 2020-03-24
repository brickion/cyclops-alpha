import cv2
import platform
import numpy as np
from uvctypes import *

def running_on_jetson_nano():
    return platform.machine() == "aarch64"

def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=640, display_height=480, framerate=60, flip_method=0):
    """
    Return an OpenCV-compatible video source description that uses gstreamer to capture video from the camera on a Jetson Nano
    """
    return (
            f'nvarguscamerasrc ! video/x-raw(memory:NVMM), ' +
            f'width=(int){capture_width}, height=(int){capture_height}, ' +
            f'format=(string)NV12, framerate=(fraction){framerate}/1 ! ' +
            f'nvvidconv flip-method={flip_method} ! ' +
            f'video/x-raw, width=(int){display_width}, height=(int){display_height}, format=(string)BGRx ! ' +
            'videoconvert ! video/x-raw, format=(string)BGR ! appsink'
            #f'videocrop top=(int)0 left=(int)106 right=(int)107 bottom=(int)0 !' + #do crop in gstreamer later
            )

def get_ir_source(display_width=640, display_height=480):
    return (
            f'v4l2src device=/dev/video1 ! video/x-raw, format=(string)BGR ! ' +
            f'videoscale ! video/x-raw, width=(int){display_width}, height=(int){display_height} ! appsink'
            )

def main_loop():
    if running_on_jetson_nano():
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
        ir_capture = cv2.VideoCapture(get_ir_source(), cv2.CAP_GSTREAMER)
    else:
        video_capture = cv2.VideoCapture(0)
        ir_capture = cv2.VideoCapture(1)
    
    cv2.namedWindow('cams', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('cams', 1280, 480)

    while True:
        ret, frame = video_capture.read()
        ret_ir, frame_ir = ir_capture.read()
        catframe = np.concatenate((frame, frame_ir), axis=1)
        #frame[640:1280, 0 + 480] = frame_ir
        cv2.imshow('cams', catframe)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_loop()



import cv2
import face_recognition
import platform
import numpy as np
import apis, user_interface, constants, recognition
# from uvctypes import *

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
    magnification = 4

    if running_on_jetson_nano():
        video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
        ir_capture = cv2.VideoCapture(get_ir_source(), cv2.CAP_GSTREAMER)
    else:
        video_capture = cv2.VideoCapture(0)
        #ir_capture = cv2.VideoCapture(1)

    # cv2.namedWindow('cams', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow('cams', 1280, 480)

    process_this_frame = True
    face_locations = []
    modes = []

    sent = False

    while True:
        ret, frame = video_capture.read()
        #ret_ir, frame_ir = ir_capture.read()
        if process_this_frame: # process every other frame to save CPU
            # face detection
            small_frame = cv2.resize(frame, (0, 0), fx=1/magnification, fy=1/magnification)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)

        process_this_frame = not process_this_frame

        if len(face_locations) > 0:
            modes = user_interface.draw_frames(frame, face_locations, magnification)
        else:
            modes = []

        if constants.IMPORTANT_MODE in modes: # if one of the faces is important
            #face_image, encoding = recognition.get_face(rgb_small_frame, small_frame, face_locations[modes.index(constants.IMPORTANT_MODE)])
            if sent != True:
                important_faces = [face_locations[modes.index(constants.IMPORTANT_MODE)]]
                face_encodings = face_recognition.face_encodings(rgb_small_frame, important_faces)
                top, right, bottom, left = important_faces[0]
                face_image = small_frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (100, 100))
                face_hash = hash(str(face_encodings))
                key = apis.create_asset(face_hash)
                sent = True


            #detect_temp


        # temp detection
        #print(frame_ir[240][320])
        #minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(frame_ir)
        #print(maxVal)
        #img_ir = raw_to_8bit(frame_ir)
        # combine two frames
        #catframe = np.concatenate((frame, frame_ir), axis=1)
        #frame[640:1280, 0 + 480] = frame_ir
        cv2.imshow('cams', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main_loop()

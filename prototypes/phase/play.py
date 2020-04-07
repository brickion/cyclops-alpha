import cv2
import face_recognition
import platform
import numpy as np
import apis, user_interface, constants, recognition
import pickle
import time, math
from tinkerforge.ip_connection import IPConnection
from tinkerforge.bricklet_temperature_ir_v2 import BrickletTemperatureIRV2
HOST = "localhost"
PORT = 4223
UID = "Lr8"
OFFSET = 15.5

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


async def run(conf, connected, session):
    magnification = 4

    #load users

    #user object: hash, face_encoding, last_seen

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
    # ipcon = IPConnection()
    # tir = BrickletTemperatureIRV2(UID, ipcon)
    # ipcon.connect(HOST, PORT)

    frame_count = 1

    object_temperature = 0
    brick_enabled = True

    # try:
    #     object_temperature = tir.get_object_temperature()/10.0
    # except:
    #     brick_enabled = False


    # default frame per second
    fps = video_capture.get(cv2.CAP_PROP_FPS)
    fps_count = 0
    second = math.floor(time.time())

    while True:
        # calculate frames per second
        fps_count += 1
        if second != math.floor(time.time()):
            fps = fps_count
            fps_count = 0
            second = math.floor(time.time())

        ret, frame = video_capture.read()

        #flipping for mirroring
        frame = cv2.flip(frame, 1)
        frame = frame[0:720, 280:1000]

        #ret_ir, frame_ir = ir_capture.read()
        if frame_count %2 == 0: # process every other frame to save CPU
            # face detection
            small_frame = cv2.resize(frame, (0, 0), fx=1/magnification, fy=1/magnification)
            rgb_small_frame = small_frame[:, :, ::-1]
            face_locations = face_recognition.face_locations(rgb_small_frame)

        # detect every 3rd frame, and if it is connected
        if frame_count %3 == 0 and brick_enabled == True:
            object_temperature=36.6
            # object_temperature = round(tir.get_object_temperature()/10.0 + OFFSET,1)

        # process_this_frame = not process_this_frame
        frame_count = frame_count + 1

        if len(face_locations) > 0:
            modes = user_interface.detect_largest(frame, face_locations, magnification)
        else:
            modes = []

        if constants.IMPORTANT_MODE in modes: # if one of the faces is important
            #face_image, encoding = recognition.get_face(rgb_small_frame, small_frame, face_locations[modes.index(constants.IMPORTANT_MODE)])
            if sent != True:
                important_faces = [face_locations[modes.index(constants.IMPORTANT_MODE)]]
                face_encodings = face_recognition.face_encodings(rgb_small_frame, important_faces)

                # if not known
                top, right, bottom, left = important_faces[0]
                face_image = frame[top*magnification:bottom*magnification, left*magnification:right*magnification]
                face_image = cv2.resize(face_image, (350, 360))
                cv2.imwrite('hello.jpg', face_image) # POST should add image & encoding, in async
                face_hash = hash(str(face_encodings))
                # cv2 img to bytes=>with open(``)
                face_bytes = cv2.imencode('.jpg',face_image)[1].tobytes()
                key = await apis.create_asset(session, conf['api_base_url'] ,face_hash, face_encodings, face_bytes)

                # if known
                # API create event with hashed encoding
                sent = True

        user_interface.draw_guide_frame(frame, object_temperature, brick_enabled and constants.IMPORTANT_MODE in modes, fps)
        user_interface.draw_frames(frame, face_locations, magnification)

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

# if __name__ == "__main__":
#     run()

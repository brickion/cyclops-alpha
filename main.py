import face_recognition
import cv2
import numpy as np
import config
import time, math
import platform
from datetime import datetime, timedelta

def running_on_jetson_nano():
    # To make the same code work on a laptop or on a Jetson Nano, we'll detect when we are running on the Nano
    # so that we can access the camera correctly in that case.
    # On a normal Intel laptop, platform.machine() will be "x86_64" instead of "aarch64"
    return platform.machine() == "aarch64"


def get_jetson_gstreamer_source(capture_width=1280, capture_height=720, display_width=640, display_height=360, framerate=30, flip_method=0):
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
            )


NEW_EVENT_MINS = 5

if running_on_jetson_nano():
    # Accessing the camera with OpenCV on a Jetson Nano requires gstreamer with a custom gstreamer source string
    video_capture = cv2.VideoCapture(get_jetson_gstreamer_source(), cv2.CAP_GSTREAMER)
else:
    # Accessing the camera with OpenCV on a laptop just requires passing in the number of the webcam (usually 0)
    # Note: You can pass in a filename instead if you want to process a video file instead of a live camera stream
    video_capture = cv2.VideoCapture(0)

video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

# names, faces = [] #config.loadJson()
# print(str(len(names)) + ' items loaded')
# print('names loaded')
# print(names)
# print('faces loaded')
# print(faces)

# Create arrays of known face encodings and their names
known_face_encodings = []
known_face_names = []
known_face_metadata = []

def register_new_face(face_encoding, face_image):
    known_face_encodings.append(face_encoding)
    known_face_metadata.append({
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
    })

def lookup_known_face(face_encoding):
    metadata = None

    if len(known_face_encodings) == 0:
        return metadata

    face_distances = face_recognition.face_distance(
        known_face_encodings,
        face_encoding
    )

    best_match_index = np.argmin(face_distances)

    if face_distances[best_match_index] < 0.65:
        metadata = known_face_metadata[best_match_index]
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1

        if datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=NEW_EVENT_MINS):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1

    return metadata

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

fps = video_capture.get(cv2.CAP_PROP_FPS)
fps_count = 0

print(fps)
second = math.floor(time.time())
while True:
    fps_count += 1
    if second != math.floor(time.time()):
        fps = fps_count
        fps_count = 0
        second = math.floor(time.time())

    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Resize frame of video to 1/4 size for faster face recognition processing
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

    # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
    rgb_small_frame = small_frame[:, :, ::-1]

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_labels = []
        for face_location, face_encoding in zip(face_locations, face_encodings):
            # See if this face is in our list of known faces.
            metadata = lookup_known_face(face_encoding)

            # If we found the face, label the face with some useful information.
            if metadata is not None:
                time_at_location = datetime.now() - metadata['first_seen_this_interaction']
                face_label = f"At location {int(time_at_location.total_seconds())}s"

            # If this is a brand new face, add it to our list of known faces
            else:
                face_label = "New person!"

                # Grab the image of the the face from the current frame of video
                top, right, bottom, left = face_location
                face_image = small_frame[top:bottom, left:right]
                face_image = cv2.resize(face_image, (150, 150))

                # Add the new face to our known face data
                register_new_face(face_encoding, face_image)

            face_labels.append(face_label)
            #print(face_label)

    process_this_frame = not process_this_frame

    font = cv2.FONT_HERSHEY_DUPLEX
    # Display the results
    for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 1)

        # Draw a label with a name below the face
        #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 255, 255), cv2.FILLED)

        #cv2.putText(frame, face_label, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
        face_image = frame[top:bottom, left:right]

        # Put the blurred face region back into the frame image
        frame[top:bottom, left:right] = face_image

    cv2.putText(frame, str(fps) + ' fps', (5, 22), font, 0.5, (0, 255, 0), 1)
    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        #save_known_faces()
        break

    # if len(face_locations) > 0 and number_of_faces_since_save > 100:
    #     save_known_faces()
    #     number_of_faces_since_save = 0
    # else:
    #     number_of_faces_since_save += 1

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

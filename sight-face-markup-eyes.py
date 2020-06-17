import face_recognition
import cv2
import numpy as np
import config
import time, math
from datetime import datetime, timedelta

NEW_EVENT_MINS = 5

video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 600)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 400)

names, faces = config.loadJson()
print(str(len(names)) + ' items loaded')
print('names loaded')
print(names)
print('faces loaded')
print(faces)

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

        # face_names = []
        # for face_encoding in face_encodings:
        #     # See if the face is a match for the known face(s)
        #     matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
        #     name = "Unknown"
        #
        #     # # If a match was found in known_face_encodings, just use the first one.
        #     # if True in matches:
        #     #     first_match_index = matches.index(True)
        #     #     name = known_face_names[first_match_index]
        #
        #     # Or instead, use the known face with the smallest distance to the new face
        #     face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
        #     best_match_index = np.argmin(face_distances)
        #     if matches[best_match_index]:
        #         name = known_face_names[best_match_index]
        #
        #     face_names.append(name)
        #     print(name + ' detectd at ' + str(second))

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
                #register_new_face(face_encoding, face_image)

            face_labels.append(face_label)
            #print(face_label)

    #process_this_frame = not process_this_frame

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
        face_landmarks_list = face_recognition.face_landmarks(face_image)
        for face_landmarks in face_landmarks_list:
            points_l = np.array([face_landmarks['left_eye'][1], face_landmarks['left_eye'][2], face_landmarks['left_eye'][4], face_landmarks['left_eye'][5]])
            points_r = np.array([face_landmarks['right_eye'][1], face_landmarks['right_eye'][2], face_landmarks['right_eye'][4], face_landmarks['right_eye'][5]])
            face_image = cv2.fillPoly(face_image, [points_l], (255,255,0))
            face_image = cv2.fillPoly(face_image, [points_r], (255,255,0))

            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][0], face_landmarks['bottom_lip'][1], (0,255,255), 5)
            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][1], face_landmarks['bottom_lip'][2], (0,255,255), 5)
            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][2], face_landmarks['bottom_lip'][3], (0,255,255), 5)
            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][3], face_landmarks['bottom_lip'][4], (0,255,255), 5)
            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][4], face_landmarks['bottom_lip'][5], (0,255,255), 5)
            face_image = cv2.line(face_image, face_landmarks['bottom_lip'][5], face_landmarks['bottom_lip'][6], (0,255,255), 5)

        #face_image = cv2.GaussianBlur(face_image, (99, 99), 30)

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

import face_recognition
import cv2
import numpy as np
import config
import time, math
from datetime import datetime, timedelta
import pickle

NEW_EVENT_MINS = 5

#######
# record faces, store them, count activation times
# 

video_capture = cv2.VideoCapture(0)
# names, faces = config.loadJson()
# print(str(len(names)) + ' items loaded')
# print('names loaded')
# print(names)
# print('faces loaded')
# print(faces)

def save_known_faces():
    with open("./data/faces.dat", "wb") as face_data_file:
        face_data = [known_face_encodings, known_face_metadata]
        pickle.dump(face_data, face_data_file)
        print("Known faces backed up to disk.")


def load_known_faces():
    global known_face_encodings, known_face_metadata

    try:
        with open("./data/faces.dat", "rb") as face_data_file:
            known_face_encodings, known_face_metadata = pickle.load(face_data_file)
            print("Known faces loaded from disk.")
    except FileNotFoundError as e:
        print("No previous face data found - starting with a blank known face list.")
        pass

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
# Create arrays of known face encodings and their names
known_face_encodings = []
known_face_names = []
known_face_metadata = []
number_of_faces_since_save = 0

load_known_faces()

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
                register_new_face(face_encoding, face_image)

            face_labels.append(face_label)

    process_this_frame = not process_this_frame


    # Display the results
    for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face_label, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)

    number_of_recent_visitors = 0
    for metadata in known_face_metadata:
        # If we have seen this person in the last minute, draw their image
        if datetime.now() - metadata["last_seen"] < timedelta(seconds=10) and metadata["seen_frames"] > 5:
            # Draw the known face image
            x_position = number_of_recent_visitors * 150
            frame[30:180, x_position:x_position + 150] = metadata["face_image"]
            number_of_recent_visitors += 1

            # Label the image with how many times they have visited
            visits = metadata['seen_count']
            visit_label = f"{visits} visits"
            if visits == 1:
                visit_label = "First visit"
            cv2.putText(frame, visit_label, (x_position + 10, 170), cv2.FONT_HERSHEY_DUPLEX, 0.6, (255, 255, 255), 1)

    if number_of_recent_visitors > 0:
        cv2.putText(frame, "Visitors at Door", (5, 18), cv2.FONT_HERSHEY_DUPLEX, 0.8, (255, 255, 255), 1)

    # cv2.putText(frame, str(fps) + ' fps', (5, 22), font, 1.0, (255, 0, 0), 1)
    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        save_known_faces()
        break

    if len(face_locations) > 0 and number_of_faces_since_save > 100:
        save_known_faces()
        number_of_faces_since_save = 0
    else:
        number_of_faces_since_save += 1

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

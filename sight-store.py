import face_recognition
import cv2
import numpy as np
import config, apis
import time, math
from datetime import datetime, timedelta

#######
# record faces, display name, count activation times
#

NEW_EVENT_MINS = 1

video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)
names, faces, metas = config.loadFaceAndMeta()
print(str(len(names)) + ' items loaded')
print(names)
print('names loaded')
print(faces)
print('faces loaded')
print(metas)
print('meta info loaded')

# Create arrays of known face encodings and their names
known_face_encodings = faces
known_face_names = names
known_face_metadata = metas

def register_new_face(face_encoding, face_image):
    known_face_encodings.append(face_encoding)
    known_face_metadata.append({
        "first_seen": datetime.now(),
        "first_seen_this_interaction": datetime.now(),
        "last_seen": datetime.now(),
        "seen_count": 1,
        "seen_frames": 1,
        "face_image": face_image,
        "name": 'unknown'
    })
    known_face_names.append({name:'unknown'})

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
        #print(metadata)
        metadata = known_face_metadata[best_match_index]
        metadata["last_seen"] = datetime.now()
        metadata["seen_frames"] += 1
        metadata["name"] = known_face_names[best_match_index]
        metadata['distance'] = face_distances[best_match_index]
        print(metadata['distance'])
        if metadata["first_seen_this_interaction"] == 0 or datetime.now() - metadata["first_seen_this_interaction"] > timedelta(minutes=NEW_EVENT_MINS):
            metadata["first_seen_this_interaction"] = datetime.now()
            metadata["seen_count"] += 1
            #print('seen')

            #apis.log_person(metadata['name'])

    #print(metadata)
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
    face_labels = []

    # Only process every other frame of video to save time
    if process_this_frame:
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)


        for face_location, face_encoding in zip(face_locations, face_encodings):
            # See if this face is in our list of known faces.
            metadata = lookup_known_face(face_encoding)
            # If we found the face, label the face with some useful information.
            if metadata is not None:
                time_at_location = datetime.now() - metadata['first_seen_this_interaction']
                likeliness = min(max(round(metadata['distance'] / 0.45 * 100), 60), 99)
                #print(round(metadata['distance'] / 0.45 * 100))
                face_label = str(metadata['name']) + ' ' + str(likeliness) + '%'

            # If this is a brand new face, add it to our list of known faces
            # else:
            #     face_label = "New!"
            #     # Grab the image of the the face from the current frame of video
            #     top, right, bottom, left = face_location
            #     face_image = small_frame[top:bottom, left:right]
            #     face_image = cv2.resize(face_image, (150, 150))
            #
            #     # Add the new face to our known face data
            #     register_new_face(face_encoding, face_image)

            face_labels.append(face_label)


    #process_this_frame = not process_this_frame

    # Display the results
    for (top, right, bottom, left), face_label in zip(face_locations, face_labels):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (255, 255, 255), 2)

        # Draw a label with a name below the face
        #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, face_label, (left + 6, bottom - 6), font, 0.5, (255, 255, 255), 1)


    cv2.putText(frame, str(fps) + ' fps', (5, 22), font, 0.5, (0, 255, 0), 1)
    # Display the resulting image
    cv2.imshow('Video', frame)

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

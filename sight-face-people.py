import face_recognition
import cv2
import numpy as np
import config
import time, math
from datetime import datetime, timedelta

NEW_EVENT_MINS = 5
font = cv2.FONT_HERSHEY_DUPLEX

video_capture = cv2.VideoCapture(0)
video_capture.set(cv2.CAP_PROP_FRAME_WIDTH, 400)
video_capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 300)

roy_image = face_recognition.load_image_file("./faces/roy_photo.jpg")
roy_face_encoding = face_recognition.face_encodings(roy_image)[0]

obama_image = face_recognition.load_image_file("./faces/obama.jpg")
obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

#print(roy_face_encoding)
known_face_encodings = [
    roy_face_encoding,
    obama_face_encoding
]

known_face_names = [
    "Roy",
    "Obama"
]

face_locations = []
face_encodings = []
face_names = []

# Create arrays of known face encodings and their names
known_face_metadata = []

def lookup_known_face(face_encoding):
    metadata = None
    distance = None

    if len(known_face_encodings) == 0:
        return metadata, distance

    face_distances = face_recognition.face_distance(
        known_face_encodings,
        face_encoding
    )

    best_match_index = np.argmin(face_distances)

    if face_distances[best_match_index] < 0.65:
        #print(known_face_names[best_match_index])
        metadata = known_face_names[best_match_index]
        distance = face_distances[best_match_index]

    return metadata, distance

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
            metadata, distance = lookup_known_face(face_encoding)
            # If we found the face, label the face with some useful information.
            if metadata is not None and distance is not None :
                #time_at_location = datetime.now() - metadata['first_seen_this_interaction']
                likeliness = min(max(round(distance / 0.45 * 100), 60), 99)
                #print(round(metadata['distance'] / 0.45 * 100))
                face_label = str(metadata) + ' ' + str(likeliness) + '%'
                print(face_encoding)

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

            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 1)
            cv2.rectangle(frame, (left, bottom - 20), (right, bottom), (0, 255, 255), cv2.FILLED)

            cv2.putText(frame, face_label, (left + 6, bottom - 6), font, 0.5, (0, 0, 0), 1)


        # face_labels = []
        # for face_location, face_encoding in zip(face_locations, face_encodings):
        #     # See if this face is in our list of known faces.
        #     metadata = lookup_known_face(face_encoding)
        #
        #     # If we found the face, label the face with some useful information.
        #     if metadata is not None:
        #         time_at_location = datetime.now() - metadata['first_seen_this_interaction']
        #         face_label = f"At location {int(time_at_location.total_seconds())}s"
        #
        #     # If this is a brand new face, add it to our list of known faces
        #     else:
        #         face_label = "New person!"
        #
        #         # Grab the image of the the face from the current frame of video
        #         top, right, bottom, left = face_location
        #         face_image = small_frame[top:bottom, left:right]
        #         face_image = cv2.resize(face_image, (150, 150))
        #
        #         # Add the new face to our known face data
        #         register_new_face(face_encoding, face_image)
        #
        #     face_labels.append(face_label)
        #     #print(face_label)

    #process_this_frame = not process_this_frame

    # font = cv2.FONT_HERSHEY_DUPLEX
    # # Display the results
    # for (top, right, bottom, left) in face_locations:
    #     # Scale back up face locations since the frame we detected in was scaled to 1/4 size
    #     top *= 4
    #     right *= 4
    #     bottom *= 4
    #     left *= 4
    #
    #     # Draw a box around the face
    #     cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 255), 1)
    #
    #     # Draw a label with a name below the face
    #     #cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (255, 255, 255), cv2.FILLED)
    #
    #     #cv2.putText(frame, face_label, (left + 6, bottom - 6), font, 0.8, (255, 255, 255), 1)
    #     face_image = frame[top:bottom, left:right]
    #
    #
    #     # Put the blurred face region back into the frame image
    #     frame[top:bottom, left:right] = face_image

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

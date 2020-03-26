import cv2
import face_recognition

def get_face(rgb_small_frame, small_frame, face_location):
    face_encodings = face_recognition.face_encodings(rgb_small_frame, [face_location])
    face_image = small_frame[face_location[0]:face_location[2], face_location[1]:face_location[3]]
    face_image = cv2.resize(face_image, (100, 100))
    return face_image, [face_encodings]

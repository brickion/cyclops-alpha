import face_recognition

def load_face(file_name):
    image = face_recognition.load_image_file(file_name)
    face_encoding = face_recognition.face_encodings(image)[0]
    return face_encoding

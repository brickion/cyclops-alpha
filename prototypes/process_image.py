import face_recognition


image = face_recognition.load_image_file('billie.jpg')
face_encoding = face_recognition.face_encodings(image)[0]
print(face_encoding.tolist())

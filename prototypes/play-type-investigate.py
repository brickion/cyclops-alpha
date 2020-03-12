import face_recognition
import numpy as np

roy_image = face_recognition.load_image_file("./faces/obama.jpg")
roy_face_encoding = face_recognition.face_encodings(roy_image)[0]

print(type(roy_face_encoding))
print(roy_face_encoding)

jsonvar = roy_face_encoding.tolist()
print(type(jsonvar))
print(jsonvar)

nparray = np.array(jsonvar)
print(type(nparray))
print(nparray)

blah = []
blah.append(nparray)

print(type(blah))
print(blah)

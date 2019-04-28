import os
import cv2
import face_recognition as fr
import face_recognition
import numpy as np
import time

def auto_encode():
    known_image_list = []
    for face_dir in os.listdir("faces"):
        new_face_dir = "faces/" + str(face_dir)
        known_image_list.append(new_face_dir)


video_capture = cv2.VideoCapture(0)
aadit_image = face_recognition.load_image_file("faces/Aadit.jpg")
aadit_face_encoding = face_recognition.face_encodings(aadit_image)[0]
known_face_encodings = [
    aadit_face_encoding,
]
known_face_names = [
    "Aadit Trivedi",
]
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

for counter in range(0,5):
    ret, frame = video_capture.read()
    small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb_small_frame = small_frame[:, :, ::-1]
    if process_this_frame:
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)
        face_names = []
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
            face_names.append(name)
            os.system('espeak "' + name + ' has been detected"')
            print(name + " has been detected")
    counter = counter + 1
    time.sleep(1)

    process_this_frame = not process_this_frame
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

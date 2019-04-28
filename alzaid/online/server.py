import face_recognition
from flask import Flask, render_template, Response, redirect, url_for, render_template, request, flash
import cv2
import numpy as np
import time
import webbrowser
from werkzeug.utils import secure_filename
import os
from flask_googlemaps import GoogleMaps
from flask_googlemaps import Map
from geopy.geocoders import Nominatim
geolocator = Nominatim(user_agent="aljvhjgkhz")
import add_faces
from add_faces import *

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['GOOGLEMAPS_KEY'] = "8JZ7i18MjFuM35dJHq70n3Hx4"
GoogleMaps(app)

vc = cv2.VideoCapture(0)

@app.route('/')
def land():
    return render_template('landing.html')



@app.route('/login')
def login():
    return render_template('login.html')

def gen():
    global logged_in
    logged_in = False
    global x_counter
    x_counter = 0
    person_in_frame = ""
    process_this_frame = True
    while True:
        x_counter = x_counter + 1
        rval, frame = vc.read()
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
        process_this_frame = not process_this_frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            if x_counter > 30 and logged_in == False:
                person_in_frame = name
                print(person_in_frame)
                url = "http://localhost:5000/home/"+str(name)
                webbrowser.open(url)
                logged_in = True
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')

def gen_detect():
    global has_spoken
    has_spoken = False
    global x_counter
    x_counter = 0
    person_in_frame = ""
    process_this_frame = True
    while True:
        x_counter = x_counter + 1
        rval, frame = vc.read()
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
        process_this_frame = not process_this_frame
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
            if x_counter > 30 and has_spoken == False:
                person_in_frame = name
                print(person_in_frame)
                os.system('espeak "' + name + ' has been detected"')
                has_spoken = True
        cv2.imwrite('t.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('t.jpg', 'rb').read() + b'\r\n')


@app.route("/detect", methods=['GET','POST'])
def detect():
    return render_template('detect.html')


@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
@app.route('/video_detect')
def video_detect():
    return Response(gen_detect(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/home/<user_name>')
def home(user_name):
    return render_template('home.html', user_name=user_name, face_list=os.listdir('static/faces/' + user_name))

@app.route('/game')
def game():
    return render_template('index.html')

@app.route('/register', methods=['GET', 'POST'])
def upload_file():
    if request.method == 'POST':
        """
        user_address = request.form['address']
        location = geolocator.geocode(str(user_address))
        my_lat = location.latitude
        my_lon = location.longitude
        print(my_lat)
        print(my_lon)

        mymap = Map(
            identifier="view-side",
            lat=my_lat,
            lng=my_lon,
            markers=[(my_lat, my_lon)]
        )

"""

        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            add_faces.add_user_directory(str(request.form['name']))
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            new_image = face_recognition.load_image_file("static/faces/" + filename)
            new_encoding = face_recognition.face_encodings(new_image)[0]
            known_face_encodings.append(new_encoding)
            known_face_names.append(request.form['name'])
            return render_template('home.html', user_name=str(request.form['name']), face_list=os.listdir('static/faces/' + request.form['name']))
    return render_template('register.html')

@app.route('/upload/<user_name>', methods=['GET', 'POST'])
def upload(user_name):
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        if file:
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'] + user_name + '/' + request.form['name'] + '.jpg'))
            new_image = face_recognition.load_image_file("static/faces/" + user_name + '/' + request.form['name'] + '.jpg')
            new_encoding = face_recognition.face_encodings(new_image)[0]
            known_face_encodings.append(new_encoding)
            known_face_names.append(request.form['name'])
            return render_template('home.html', user_name=user_name, face_list=os.listdir('static/faces/' + user_name))
    return render_template('home.html', user_name=user_name, face_list=os.listdir('static/faces/' + user_name))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, threaded=True)

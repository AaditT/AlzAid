import face_recognition
from flask import Flask, render_template, Response, redirect, url_for, render_template, request, flash
import cv2
import numpy as np
import time
import webbrowser
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = 'static/faces/'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png'])

global process_this_frame
global aadit_image
global aadit_encoding
global known_face_encodings
global known_face_names
global face_locations
global face_encodings
global face_names
global person_in_frame

process_this_frame = True
aadit_image = face_recognition.load_image_file("static/faces/Aadit.jpg")
aadit_encoding = face_recognition.face_encodings(aadit_image)[0]
known_face_encodings = [
    aadit_encoding
]
known_face_names = [
    "Aadit"
]
face_locations = []
face_encodings = []
face_names = []
person_in_frame = ""

def add_user_directory(name):
    try:
        os.mkdir('static/faces/' + name)
    except:
        return
def add_user_image(owner, image, name):
    print('mv ' + image + ' static/faces/' + owner + '/' + name + '.jpg')
    os.system('mv ' + image + ' static/faces/' + owner + '/' + name + '.jpg')

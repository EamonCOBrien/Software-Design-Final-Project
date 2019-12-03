from flask import Flask, render_template, request, Response
from opencv_camera import Camera
import time
import numpy as np
from mini_project_4 import Model, Controller, View, process_frame
import os
import cv2

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home_screen.html')

@app.route('/intro')
def introduction():
    return render_template('intro.html')

@app.route('/story')
def story():
    return render_template('story.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/draw')
def draw():
    model.calibration_start = time.time()
    return render_template('stream.html')

@app.route('/video_feed')
def video_feed():
    """Video streaming route. Put this in the src attribute of an img tag."""
    return Response(gen(Camera()),
        mimetype='multipart/x-mixed-replace; boundary=frame')

def gen(camera): # i think this is where we would run all of our original code
    """Video streaming generator function."""
    while True:
        frame = camera.get_frame() # get the frame in binary from Opencv
        frame = np.frombuffer(frame, np.uint8) # turn the binary into an array
        frame = cv2.imdecode(frame, cv2.IMREAD_UNCHANGED) # turn the array into an image
        model.frame = frame
        process_frame(model, controller, view) # run MP4 on the image
        frame = cv2.imencode('.jpg', model.frame)[1].tobytes() # turn the image back into binary
        yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n') # send the binary to the web app

if __name__ == '__main__':
    model = Model()
    view = View(model)
    controller = Controller(model)
    HOST = '0.0.0.0' if 'PORT' in os.environ else '127.0.0.1'
    PORT = int(os.environ.get('PORT', 5000))
    app.run(host=HOST, port=PORT)

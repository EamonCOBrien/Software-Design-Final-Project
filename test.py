from flask import Flask, render_template, request, Response
from opencv_camera import Camera
import cv2

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('home_screen.html')

@app.route('/intro')
def introduction():
    return render_template('intro.html')

@app.route('/rules')
def rules():
    return render_template('rules.html')

@app.route('/draw')
def draw():
   return render_template('stream.html')

def gen(camera): # i think this is where we would run all of our original code
 """Video streaming generator function."""
 while True:
     frame = camera.get_frame() #this is the frame we would draw on
     # unfortunately, it is stored as bytes, and i don't know how to work with that
     yield (b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
 """Video streaming route. Put this in the src attribute of an img tag."""
 return Response(gen(Camera()),
                 mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == '__main__':
    app.run()

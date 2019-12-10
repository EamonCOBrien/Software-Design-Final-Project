# Software-Design-Final-Project

CVPaint is a web app that uses openCV to allow a user to draw on their computer screen through their camera. It uses Flask and OpenCV for the core drawing capabilities, and the Camera class written by Miguel Grinberg to handle streaming the feed to a browser. (https://blog.miguelgrinberg.com/post/flask-video-streaming-revisited)

Authors: Eamon O'Brien, Gail Romer, Cali Wierzbanowski

## Instructions:

CVPaint runs on a browser, hosted on your device. Follow these steps to access it.

1) Clone the repository into a folder on your device: git clone https://github.com/EamonCOBrien/Software-Design-Final-Project.git

2) Install the necessary packages:
	pip install opencv-python
	pip install imutils
	pip install flask

3) In the installed directory, run: python CVpaint.py

4) Go to http://127.0.0.1:5000/. You will see the website for the project. The How to Play page of the site includes instructions on how to use the drawing program itself, if you get stuck using a feature. Click Start on the top navigation bar to begin.

Want to contribute or have questions? E-mail cwierzbanowski@olin.edu with ideas and additions.

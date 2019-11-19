# Software-Design-Final-Project

CVPaint: CVPaint is a fun, artistic, and interactive program that anyone, anywhere can use and enjoy.

CVPaint is a web app that uses openCV, flask, and heroku to allow a user to "paint" on their computer screen through their camera using a colored "wand". The wand can be any colored object that constrasts with the background. This is because our program uses color tracking through openCV to identify the location of the "wand" and then use the tracking information to draw on th sreen.

Authors: Eamon O'Brien, Gail Romer, Cali Wierzbanowski
References: 

Instructions: The entire program is contained in a global web app. It can be accessed at the url: https://drawing-program-demo.herokuapp.com/. Computer must have access to a camera. Further instructions are linked on the website.

Usage: If you prefer to download the code and run it locally, here's how: 
1) Git clone Software-Design-Final-Project from github and run mini_project_4.py.

2) To install packages, run:
	pip install opencv-python
	pip install imutils

3) To run the drawing program, make sure you have all the button icons, buttons.py, and drawing_program.py in the same folder, and run drawing_program.py.

4) Calibration takes pixel from the center of the circle. To properly calibrate, the colored wand must cover the center of the circle. Better lighting gives better results.

Licensing?

Want to contribute or have questions? E-mail cwierzbanowski@olin.edu with ideas and additions.

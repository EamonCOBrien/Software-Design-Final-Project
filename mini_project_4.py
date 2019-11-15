import cv2
import numpy as np
import time
import imutils
import os
from buttons import *

class Model:
    """
    Class that keeps track of what is going on in the program. It knows the current color
    of the drawing tool, and things like whether the program should be quitting. Also,
    the init of the model is where the elements of the interface are created (not displayed)
    """
    def __init__(self):
        self.upper_color_1 = np.zeros(1)
        self.lower_color_1 = np.zeros(1)
        self.upper_color_2 = np.zeros(1)
        self.lower_color_2 = np.zeros(1)
        self.calibration_start = 0
        self.elapsed_time = 0
        self.calibration_time = 6
        self.current_path = os.path.dirname(__file__)
        self.line_points = []
        self.cursor_1 = ()
        self.cursor_2 = ()
        self.pen_size = 5
        self.eraser_size = self.pen_size + 1 #6
        self.line_colors = {'black' : (0,0,0), 'red' : (0,0,255), 'green' : (0,255,0), 'blue' : (255,0,0), 'grey' : (190,190,190)}
        self.line_color = 'black'
        self.tool = 'calibrate'
        self.shape_started = False
        self.save = Save_Button(20,20,'Save.png',50,self)
        self.clear = Clear_Button(90,20,'Clear.png',50, self)
        self.erase = Erase_Button(160,20,'Erase.png',50, self, 'grey', self.eraser_size)
        self.red = Color_Button(230,20,'Red.png',50, self, 'red', self.pen_size)
        self.blue = Color_Button(300,20,'Blue.png',50, self,'blue', self.pen_size)
        self.green = Color_Button(370,20,'Green.png',50, self,'green', self.pen_size)
        self.black = Color_Button(440,20,'Black.png',50, self,'black', self.pen_size)
        self.calibrate = Calibration_Button(510,20,'Calibrate.png',50, self)
        self.shape = Shape_Button(580,20,'Shape.png',50, self)
        self.thin = Thickness_Button(160,250,'Thin.png',50,self,2)
        self.medium = Thickness_Button(300,250,'Medium.png',50,self,7)
        self.thick = Thickness_Button(440,250,'Thick.png',50,self,15)
        #self.exit = Exit_Button(650,20,'Exit.png',50, self)


    def check_buttons(self, cursor):
        """
        Add the current position of the cursor to points and checks if it is in
        the area of any of the buttons.
        """
        self.clear.check_pressed(cursor)
        self.save.check_pressed(cursor)
        self.red.check_pressed(cursor)
        self.blue.check_pressed(cursor)
        self.green.check_pressed(cursor)
        self.black.check_pressed(cursor)
        #self.exit.check_pressed(cursor)
        self.erase.check_pressed(cursor)
        self.calibrate.check_pressed(cursor)
        self.shape.check_pressed(cursor)
        if self.tool == 'thickness':
            self.thin.check_pressed(cursor)
            self.medium.check_pressed(cursor)
            self.thick.check_pressed(cursor)

class Controller:
    """
    A class to detect input from the user of the program. It takes the model as input, and has a
    function to return the position of an object of the color from the calibration step
    """
    def __init__(self, model):
        self.model = model

    def check_distance(self, point):
        if self.model.line_points:
            if self.model.line_points[-1]:
                x1 = point[0]
                y1 = point[1]
                x2 = self.model.line_points[-1][0]
                y2 = self.model.line_points[-1][1]
                distance = np.sqrt((x2-x1)**2 + (y2-y1)**2)
                return distance
        else:
            return 0


    def detect_wand(self, frame, lower, upper):
        """
        Looks at the current frame, finds the largest contour of the target color,
        and returns its center
        """
        kernel = np.ones((15, 15), 'uint8') # make a kernel for blurring
        blurred = cv2.GaussianBlur(frame, (17, 17), 0)
        blurred = cv2.dilate(frame, kernel) # blur the frame to average out the value in the circle
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv_frame, lower, upper)
        contours = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contours = imutils.grab_contours(contours)
        center = None

        if len(contours) > 0:
            largest_contour = max(contours, key=cv2.contourArea)
            ((x, y), radius) = cv2.minEnclosingCircle(largest_contour)
            M = cv2.moments(largest_contour)
            if M["m00"] != 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
            else:
                center = (0,0)

            if radius > 30:
                velocity = self.check_distance(center)
                return((center[0], center[1],self.model.line_color, velocity,self.model.pen_size)) #Tuple where line info is stored)
            else:
                return False

class View:
    """
    Class that creates and then draws on the display. Here is where you draw draw_lines
    and tell the program to display interface elements. If we add future tools besides the line,
    it will go here.
    """
    def __init__(self, model):
        self.model = model

    def show_lines(self, frame):
        """
        Iterates through all the points in the list of where the target has been
        and draws lines between them.
        """
        for i in range(len(self.model.line_points)):
            if i > 0 and self.model.line_points[i-1] and self.model.line_points[i]: # make sure both endpoints exist
                if self.model.line_points[i][3] < 100: # check the velocity of the target to filter out false positives
                    cv2.line(frame, self.model.line_points[i-1][0:2], self.model.line_points[i][0:2], self.model.line_colors[self.model.line_points[i][2]], self.model.pen_size)
        return frame

    def remove_lines(self,frame):
        if self.model.cursor_1 and self.model.line_points:
            eraser_range_x = [i for i in range(int(self.model.cursor_1[0])-5, int(self.model.cursor_1[0])+self.model.eraser_size)]
            eraser_range_y = [i for i in range(int(self.model.cursor_1[1])-5, int(self.model.cursor_1[1])+self.model.eraser_size)]
            for i in range(len(self.model.line_points)):
                if self.model.line_points[i]:
                    if self.model.line_points[i][0] in eraser_range_x and self.model.line_points[i][1] in eraser_range_y:
                        self.model.line_points[i] = False


    def show_interface(self, frame):
        """
        Calls the display function of all the buttons.
        """
        self.model.save.display(frame)
        self.model.clear.display(frame)
        self.model.red.display(frame)
        self.model.blue.display(frame)
        self.model.green.display(frame)
        self.model.black.display(frame)
        #self.model.exit.display(frame)
        self.model.erase.display(frame)
        self.model.calibrate.display(frame)
        self.model.shape.display(frame)
        if self.model.tool == 'thickness':
            #blur current page?
            self.model.thin.display(frame)
            self.model.medium.display(frame)
            self.model.thick.display(frame)
#TODO: #if line color/eraser buttons are pressed, apply opaque mask, show line thickness buttons -------------------------
        if self.model.cursor_1: #drawing cursor
            cv2.circle(frame, ((self.model.cursor_1[0]),(self.model.cursor_1[1])),8,self.model.line_colors[self.model.line_color], thickness = 3)
        if self.model.cursor_2: #selecting cursor
            cv2.circle(frame, ((self.model.cursor_2[0]),(self.model.cursor_2[1])),8,self.model.line_colors[self.model.line_color], thickness = 2)
        return frame

#TODO: fix calibration so that it doesn't ask for green side twice.

def process_frame(frame, model, controller, view):
    frame = cv2.flip(frame,1) # reverse the frame so people aren't confused
    if model.tool == 'calibrate' and model.elapsed_time < model.calibration_time:
        model.elapsed_time = time.time() - model.calibration_start
        cv2.putText(frame,'Place green in center:' + str(int(model.calibration_time - model.elapsed_time)),(30,20),cv2.FONT_HERSHEY_DUPLEX,1,(255, 255, 255))
        cv2.circle(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), 50,(255,255,255), thickness = 3)
        cv2.circle(frame, (int(frame.shape[1]/2), int(frame.shape[0]/2)), 55,(0,0,0), thickness = 3)
    if model.tool == 'calibrate' and model.elapsed_time > model.calibration_time:
        kernel = np.ones((15, 15), 'uint8') # make a kernel for blurring
        frame = cv2.dilate(frame, kernel) # blur the frame to average out the value in the circle
        frame = cv2.GaussianBlur(frame, (17, 17), 0)
        hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        pixel = hsv_frame[int(frame.shape[0]/2), int(frame.shape[1]/2)] # grab the pixel from the center of the calibration circle
        if not model.upper_color_1.any():
            model.lower_color_1, model.upper_color_1 = (np.array([pixel[0]-10,50,50]), np.array([pixel[0]+10,250,250]))
            model.elapsed_time = 0
            model.calibration_start = time.time()
        elif not model.upper_color_2.any():
            model.lower_color_2, model.upper_color_2 = (np.array([pixel[0]-10,50,50]), np.array([pixel[0]+10,250,250]))
            model.tool = 'draw'
    if model.tool != 'calibrate':
        model.cursor_1 = controller.detect_wand(frame, model.lower_color_1, model.upper_color_1)
        model.cursor_2 = controller.detect_wand(frame, model.lower_color_2, model.upper_color_2)
        if model.tool == 'draw':
            model.line_points.append(model.cursor_1)
        if model.tool == 'erase':
            view.remove_lines(frame)

        model.check_buttons(model.cursor_2)

        frame = view.show_lines(frame)

        frame = view.show_interface(frame)

    return frame

def main_loop():
    model = Model()
    view = View(model)
    controller = Controller(model)
    cap = cv2.VideoCapture(0)
    model.calibration_start = time.time()
    while True:
        ret, frame = cap.read() # get a frame from the camera
        frame = process_frame(frame, model,controller,view)
        #if model.tool == 'rectangle':
            #if not shape_started and model.cursor_1:
                #model.shape_started = True
                #model.shape_point_1 = (model.cursor_1[0]-1, model.cursor_1[1]-1)
            #if cursor_1 and shape_started:
                #cv2.rectangle(frame, )
            #if shape_started and cursor_2:
                #model.line_points.append(rectangle points)
                #model.tool == 'draw'
        cv2.imshow('art!',frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or model.tool == 'exit':
            cap.release()
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    main_loop()

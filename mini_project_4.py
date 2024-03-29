import numpy as np
import time
import imutils
import os
from buttons import *
import cv2

class Model:
    """
    Class that keeps track of what is going on in the program. It knows the current color
    of the drawing tool, and things like whether the program should be quitting. Also,
    the init of the model is where the elements of the interface are created (not displayed)
    """
    def __init__(self):
        self.frame = None
        self.upper_color_1 = np.zeros(1)
        self.lower_color_1 = np.zeros(1)
        self.upper_color_2 = np.zeros(1)
        self.lower_color_2 = np.zeros(1)
        self.calibration_start = 0
        self.elapsed_time = 0
        self.calibration_time = 6
        self.current_path = os.path.dirname(__file__)
        self.line_points = []
        self.rectangle_points = []
        self.ellipse_points = []
        self.cursor_1 = ()
        self.cursor_2 = ()
        self.pen_size = 7
        self.eraser_size = 8
        self.line_color = (0,0,0) # the drawing color starts as black
        self.tool = 'calibration color 1'
        self.shape_started = False

        # All the buttons in the interface initialized here.

        self.clear = Clear_Button(20,20,'Clear.png',50, self)
        self.erase = Erase_Button(160,20,'Erase.png',50, self)
        self.pen = Pen_Button(90,20,'Pen.png',50,self)
        self.thicknessess = Thicknessess_Button(230,20,'Thickness.png',50, self, self.pen_size)
        self.color = Color_Button(300,20,'Color.png',50, self)
        self.rectangle = Rectangle_Button(370,20,'Rectangle.png',50,self)
        self.ellipse = Ellipse_Button(440,20,'Ellipse.png',50,self)
        self.calibrate = Calibration_Button(510,20,'Calibrate.png',50, self)

        self.draw_thin = Thickness_Button(160,200,'Thin.png',50,self,2)
        self.draw_medium = Thickness_Button(300,200,'Medium.png',50,self,7)
        self.draw_thick = Thickness_Button(440,200,'Thick.png',50,self,15)
        self.color_slider = Color_Slider(40,205,"ColorBar.png",42,500,self)
        self.color_choice = Color_Choice(540,200, 'Check.png', 50, self)

    def check_buttons(self, cursor):
        """
        Just tells all of the buttons currently displayed to check if the cursor
        is over them.
        """
        if self.tool == 'thickness':
            self.draw_thin.check_pressed(cursor)
            self.draw_medium.check_pressed(cursor)
            self.draw_thick.check_pressed(cursor)
        elif self.tool == 'color_slider':
            self.color_slider.check_pressed(cursor)
            self.color_choice.check_pressed(cursor)
        else:
            self.thicknessess.check_pressed(cursor)
            self.clear.check_pressed(cursor)
            self.color.check_pressed(cursor)
            self.rectangle.check_pressed(cursor)
            self.ellipse.check_pressed(cursor)
            self.erase.check_pressed(cursor)
            self.calibrate.check_pressed(cursor)
            self.pen.check_pressed(cursor)

class Controller:
    """
    A class to detect input from the user of the program. It takes the model as input, and has a
    function to return the position of an object of the color from the calibration step
    """
    def __init__(self, model):
        self.model = model

    def check_distance(self, point):
        """
        Checks if a point is within a certain distance of the last point in line_points.
        This gets rid of false positives far away from where the cursor was last frame.
        """
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

    def detect_wand(self, lower, upper):
        """
        Looks at the current frame, finds the largest contour of the target color,
        and returns the center of that point, as well as the current color and
        velocity of the cursor.
        """
        kernel = np.ones((15, 15), 'uint8') # make a kernel for blurring
        blurred = cv2.GaussianBlur(self.model.frame, (17, 17), 0)
        blurred = cv2.dilate(self.model.frame, kernel) # blur the frame to average out the value in the circle
        hsv_frame = cv2.cvtColor(self.model.frame, cv2.COLOR_BGR2HSV)
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

    def show_lines(self):
        """
        Iterates through all the points in the list of where the target has been
        and draws lines between them.
        """
        for i in range(len(self.model.line_points)):
            if i > 0 and self.model.line_points[i-1] and self.model.line_points[i]: # make sure both endpoints exist
                #if points[i][3] < 100: # check the velocity of the target to filter out false positives
                cv2.line(self.model.frame, self.model.line_points[i-1][0:2], self.model.line_points[i][0:2], self.model.line_points[i][2], self.model.line_points[i][-1])

    def show_rectangles(self):
        """
        Iterates through all the points in the list of where the target has been
        and draws rectangles between them.
        """
        for i in range(len(self.model.rectangle_points)):
            if i > 0 and self.model.rectangle_points[i-1] and self.model.rectangle_points[i]: # make sure both endpoints exist
                #if points[i][3] < 100: # check the velocity of the target to filter out false positives
                cv2.rectangle(self.model.frame, self.model.rectangle_points[i-1][0:2], self.model.rectangle_points[i][0:2], self.model.rectangle_points[i][2], self.model.rectangle_points[i][-1])

    def show_circles(self):
        """
        Iterates through all tfhe points in the list of where the target has been
        and draws ellipses between them.
        """
        for i in range(len(self.model.ellipse_points)):
            if i > 0 and self.model.ellipse_points[i-1] and self.model.ellipse_points[i]: # make sure both endpoints exist
                if self.model.ellipse_points[i-1][2]:
                    cv2.circle(self.model.frame, self.model.ellipse_points[i-1][0:2], self.model.ellipse_points[i], self.model.ellipse_points[i-1][2], self.model.ellipse_points[i-1][-1])

    def remove_lines(self):
        """
        This is the function called by the eraser tool. It erases lines by removing points
        from the line_points list if they are within a certain distance from the cursor.
        """
        if self.model.cursor_1 and self.model.line_points:
            eraser_range_x = [i for i in range(int(self.model.cursor_1[0])-self.model.eraser_size, int(self.model.cursor_1[0])+self.model.eraser_size)]
            eraser_range_y = [i for i in range(int(self.model.cursor_1[1])-self.model.eraser_size, int(self.model.cursor_1[1])+self.model.eraser_size)]
            for i in range(len(self.model.line_points)):
                if self.model.line_points[i]:
                    if self.model.line_points[i][0] in eraser_range_x and self.model.line_points[i][1] in eraser_range_y:
                        self.model.line_points[i] = False


    def show_interface(self):
        """
        Calls the display function of all the buttons currently in the interface
        """
        if self.model.tool != 'calibration color 1' and self.model.tool != 'calibration color 2':
            if self.model.tool == 'thickness':
                cv2.rectangle(self.model.frame,(0,250),(self.model.frame.shape[1],200),(255,255,255),-1)
                self.model.draw_thin.display(self.model.frame)
                self.model.draw_medium.display(self.model.frame)
                self.model.draw_thick.display(self.model.frame)
            elif self.model.tool == 'color_slider':
                self.model.color_slider.display(self.model.frame)
                self.model.color_choice.display(self.model.frame)
            else:
                cv2.rectangle(self.model.frame,(0,0),(self.model.frame.shape[1],90),(255,255,255),-1)
                self.model.clear.display(self.model.frame)
                self.model.thicknessess.display(self.model.frame)
                self.model.color.display(self.model.frame)
                self.model.erase.display(self.model.frame)
                self.model.calibrate.display(self.model.frame)
                self.model.color.display(self.model.frame)
                self.model.pen.display(self.model.frame)
                self.model.ellipse.display(self.model.frame)
                self.model.rectangle.display(self.model.frame)

    def show_cursor(self):
        """
        Shows a circle on the screen where the cursor is. The circle matches the current thickness
        and color of the cursor. If the current tool is erase, the circle is grey instead.
        """
        if self.model.tool == 'erase':
            if self.model.cursor_1: #drawing cursor
                cv2.circle(self.model.frame, ((self.model.cursor_1[0]),(self.model.cursor_1[1])),self.model.pen_size,(190,190,190), thickness = 2)
            if self.model.cursor_2: #selecting cursor
                cv2.circle(self.model.frame, ((self.model.cursor_2[0]),(self.model.cursor_2[1])),self.model.pen_size,(190,190,190), thickness = 2)
        else:
            if self.model.cursor_1: #drawing cursor
                cv2.circle(self.model.frame, ((self.model.cursor_1[0]),(self.model.cursor_1[1])),self.model.pen_size,self.model.line_color, thickness = 2)
            if self.model.cursor_2: #selecting cursor
                cv2.circle(self.model.frame, ((self.model.cursor_2[0]),(self.model.cursor_2[1])),self.model.pen_size,self.model.line_color, thickness = 2)

def process_frame(model, controller, view):
    """
    This function finds the cursors, executes what current tool needs to happen,
    shows all the buttons, and draws on the frame.
    """
    model.frame = cv2.flip(model.frame,1) # reverse the frame so people aren't confused
    model.cursor_1 = controller.detect_wand(model.lower_color_1, model.upper_color_1) # find both cursors
    model.cursor_2 = controller.detect_wand(model.lower_color_2, model.upper_color_2)

    if model.tool == 'calibration color 1' or model.tool =='calibration color 2': # all this code only needs to run if the program is currently calibrating
        model.elapsed_time = time.time() - model.calibration_start
        if model.elapsed_time < model.calibration_time:
            cv2.putText(model.frame,'Place '+ model.tool + ' in center:' + str(int(model.calibration_time - model.elapsed_time)),(30,30),cv2.FONT_HERSHEY_DUPLEX,1,(255, 255, 255))
            cv2.circle(model.frame, (int(model.frame.shape[1]/2), int(model.frame.shape[0]/2)), 50,(255,255,255), thickness = 3)
            cv2.circle(model.frame, (int(model.frame.shape[1]/2), int(model.frame.shape[0]/2)), 55,(0,0,0), thickness = 3)
        elif model.elapsed_time > model.calibration_time:
            kernel = np.ones((15, 15), 'uint8') # make a kernel for blurring
            model.frame = cv2.dilate(model.frame, kernel) # blur the frame to average out the value in the circle
            model.frame = cv2.GaussianBlur(model.frame, (17, 17), 0)
            hsv_frame = cv2.cvtColor(model.frame, cv2.COLOR_BGR2HSV)
            pixel = hsv_frame[int(model.frame.shape[0]/2), int(model.frame.shape[1]/2)] # grab the pixel from the center of the calibration circle
            if model.tool == 'calibration color 1':
                model.lower_color_1, model.upper_color_1 = (np.array([pixel[0]-10,50,50]), np.array([pixel[0]+10,250,250]))
                model.elapsed_time = 0
                model.calibration_start = time.time()
                model.tool = 'calibration color 2'
            elif model.tool =='calibration color 2':
                model.lower_color_2, model.upper_color_2 = (np.array([pixel[0]-10,50,50]), np.array([pixel[0]+10,250,250]))
                model.tool = 'draw'

    elif model.tool == 'draw':
        model.line_points.append(model.cursor_1) # if the program is drawing, it simply needs to add to the list of points to be drawn.

    elif model.tool == 'erase':
        view.remove_lines()

    elif model.tool == 'rectangle_1':
        if model.cursor_1:
            model.rectangle_points.append(model.cursor_1)
            model.tool = 'rectangle_2'

    elif model.tool == 'rectangle_2':
        if model.cursor_1:
            cv2.rectangle(model.frame, model.rectangle_points[-1][0:2], model.cursor_1[0:2],model.rectangle_points[-1][2], model.rectangle_points[-1][-1])
        else:
            model.rectangle_points.append(model.cursor_2)
            model.rectangle_points.append(False)
            model.tool = 'rectangle_1'

    elif model.tool == 'circle_1':
        if model.cursor_1:
            model.ellipse_points.append(model.cursor_1)
            model.tool = 'circle_2'

    elif model.tool == 'circle_2':
        if model.cursor_1:
            radius = int(((model.ellipse_points[-1][0]-model.cursor_1[0])**2 + (model.ellipse_points[-1][1]-model.cursor_1[1])**2)**(1/2))
            cv2.circle(model.frame, model.ellipse_points[-1][0:2], radius, model.ellipse_points[-1][2], model.ellipse_points[-1][-1])
        elif model.cursor_2:
            radius = int(((model.ellipse_points[-1][0]-model.cursor_2[0])**2 + (model.ellipse_points[-1][1]-model.cursor_2[1])**2)**(1/2))
            model.ellipse_points.append(radius)
            model.ellipse_points.append(False)
            model.tool = 'circle_1'

    model.check_buttons(model.cursor_2)

    view.show_lines()
    view.show_rectangles()
    view.show_circles()

    view.show_interface()
    view.show_cursor()

def main_loop():
    """
    If this script is run directly, this loop takes care of making a window for the
    program and initializing everything. If the program is being run as a web app,
    this function is not used.
    """
    model = Model()
    view = View(model)
    controller = Controller(model)
    cap = cv2.VideoCapture(0)
    model.calibration_start = time.time()
    while True:
        _, model.frame = cap.read() # get a frame from the camera
        process_frame(model,controller,view) # this is where all the work is done.
        cv2.imshow('art!',model.frame)
        if cv2.waitKey(1) & 0xFF == ord('q') or model.tool == 'exit':
            cap.release()
            cv2.destroyAllWindows()
            break

if __name__ == '__main__':
    # again, this doesn't run unless this script is run directly, not from the browser
    main_loop()

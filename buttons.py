import cv2
import numpy as np
import time
import imutils
import os

class Button:
    """
    A generic class for a button that does something in our drawing program.
    x and y describe the location of the upper left corner of the button.
    """
    def __init__(self,x,y,path,size,model,pressed = False):
        self.x = x
        self.y = y
        self.size = size
        self.path = path
        self.pressed = pressed
        self.model = model
        self.icon = cv2.imread(os.path.dirname(__file__) + '/Icons/' + path, -1)

    def check_pressed(self,cursor):
        if cursor:
            if cursor[0] > self.x and cursor[0] < self.x + self.size and cursor[1] > self.y and cursor[1] < self.y + self.size:
                if not self.pressed:
                    self.press()
                    self.pressed = True
            else: #Debounce
                self.pressed = False

    def display(self,frame):
        for i in range(self.size):
            for j in range(self.size):
                if self.icon[i,j][3] > 20:
                    frame[self.y+i,self.x+j] = self.icon[i,j][0:-1]
        #frame[self.y:self.y+self.size,self.x:self.x+self.size] = self.icon[0:int(self.icon.shape[0]), 0:int(self.icon.shape[1])]

class Save_Button(Button):
    """
    A class for adding a save button to the program. Inherets from Button class.
    The Save button saves current drawing to project folder as Drawing.png.
    """
    def __init__(self,x,y,path,size,model,pressed = False):
        super().__init__(x,y,path,size,model)
        self.images_counter = 0

    def press(self):
        ret, drawing = self.model.cap.read()
        drawing = cv2.flip(drawing,1)
        for i in range(len(self.model.line_points)):
            if i > 0 and self.model.line_points[i-1] and self.model.line_points[i]: # make sure both endpoints exist
                if self.model.line_points[i][3] < 50: # check the velocity of the target to filter out false positives
                    cv2.line(drawing, self.model.line_points[i-1][0:2], self.model.line_points[i][0:2], self.model.line_colors[self.model.line_points[i][2]], 5)
        cv2.imwrite(os.path.dirname(__file__) + '/' + 'Drawing'+ str(self.images_counter) + '.png',drawing)
        self.images_counter += 1

class Clear_Button(Button):
    """
    A class for adding a clear button to the program. Inherets from Button class.
    The Clear button clears current drawing from screen by emptying points, where all
    previous wand locations are stored.
    """
    def press(self):
        self.model.line_points.clear()
        self.model.line_points.append(False)

class Color_Button(Button):
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def __init__(self,x,y,path,size,model,color):
        super().__init__(x,y,path,size,model)
        self.color = color

    def press(self):
        self.model.tool = 'draw'
        self.model.line_color = self.color

class Exit_Button(Button):
    """
    A class for adding an exit button to the program. Inherets from Button class.
    The Exit button causes program to end.
    """
    def press(self):
        self.model.tool = 'exit'

class Erase_Button(Button):
    """
    A class for adding an eraser button to the program.
    """
    def press(self):
        self.model.tool = 'erase'

class Calibration_Button(Button):
    """
    A class to add the ability to recalibrate while the program is running
    """
    def press(self):
        self.model.lower_color_1, self.model.upper_color_1 = self.model.calibration("green circle")
        self.model.lower_color_2, self.model.upper_color_2 = self.model.calibration("blue circle")

class Shape_Button(Button):
    def press(self):
        #self.model.tool = 'rectangle'
        pass

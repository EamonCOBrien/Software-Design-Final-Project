import numpy as np
import time
import imutils
import os
import cv2
import colorsys

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

class Save_Button(Button):
    """
    A class for adding a save button to the program. Inherets from Button class.
    The Save button saves current drawing to project folder as Drawing.png.
    """
    def __init__(self,x,y,path,size,model,pressed = False):
        super().__init__(x,y,path,size,model)
        self.images_counter = 0

    def press(self):
        self.model.tool = 'save'

class Clear_Button(Button):
    """
    A class for adding a clear button to the program. Inherets from Button class.
    The Clear button clears current drawing from screen by emptying points, where all
    previous wand locations are stored.
    """
    def press(self):
        self.model.line_points.clear()
        self.model.line_points.append(False)
        self.model.rectangle_points.clear()
        self.model.ellipse_points.clear()

class Thicknessess_Button(Button):
    """
    THe button that lets you choose a thickness
    """
    def press(self):
        self.model.tool = 'thickness'

class Color_Button(Button):
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def press(self):
        self.model.tool = 'color_slider' #if color button is selected, change mode to thickness, line buttons will appear

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
        self.model.tool = 'calibration color 1'
        self.model.calibration_start = time.time()

class Rectangle_Button(Button):
    """
    A class for telling the program to draw rectangles.
    """
    def press(self):
        self.model.tool = 'rectangle_1'

class Ellipse_Button(Button):
    """
    A class for telling the program to draw ellipses.
    """
    def press(self):
        self.model.tool = 'circle_1'

class Thickness_Button(Button):
    """
    A class for changing the thickness of the cursor.
    """
    def __init__(self,x,y,path,size,model,pen_size):
        super().__init__(x,y,path,size,model)
        self.pen_size = pen_size

    def press(self):
        self.model.tool = 'draw' #if thickness button pressed, start drawing again
        self.model.pen_size = self.pen_size

class Pen_Button(Button):
    """
    A class for to switch back to the drawing tool
    """
    def press(self):
        self.model.tool = 'draw'

class Color_Slider():
    """
    A class for a color slider that allows the user to select a color.
    x and y describe the location of the upper left corner of the button.
    """
    def __init__(self,x,y,path,dy,dx,model,pressed = False):
        self.x = x
        self.y = y
        self.dx = dx
        self.dy = dy
        self.path = path
        self.pressed = pressed
        self.model = model
        self.icon = cv2.imread(os.path.dirname(__file__) + '/Icons/' + path, -1)
        self.selected = (0,255,0)


    def check_pressed(self,cursor):
        if cursor:
            if cursor[0] > self.x+10 and cursor[0] < self.x+10 + self.dx and cursor[1] > self.y and cursor[1] < self.y + self.dy:
                Color_Choice = ((cursor[0]-self.x-10)/499) # 1-499
                # self.selected = Color_Choice
                bgrcolor = [i * 255 for i in colorsys.hsv_to_rgb(Color_Choice, 1, 1)]
                rgbcolor = (bgrcolor[2],bgrcolor[1],bgrcolor[0])
                self.model.line_color = rgbcolor
                self.pressed=True

            else:
                self.pressed = False

    def display(self,frame):
        for i in range(self.dy):
            for j in range(self.dx):
                if self.icon[i,j][3] > 20:
                    frame[self.y+i,self.x+j] = self.icon[i,j][0:-1]

class Color_Choice(Button):
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def press(self):
        self.model.tool = 'draw' #if eraser thickness button pressed, start erasing again


    def display(self,frame):
        cv2.rectangle(self.model.frame,(self.x,self.y),(self.x+self.size,self.y+self.size), self.model.line_color,-1) # makes the button the current color of the cursor
        for i in range(self.size): # puts the check mark icon over top of the colored rectangle
            for j in range(self.size):
                if self.icon[i,j][3] > 20:
                    frame[self.y+i,self.x+j] = self.icon[i,j][0:-1]

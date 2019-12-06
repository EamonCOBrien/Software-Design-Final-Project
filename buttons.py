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
        self.model.circle_points.clear()

class Thicknessess_Button(Button):
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def __init__(self,x,y,path,size,model,pen_size):
        super().__init__(x,y,path,size,model)
        # self.color = color
        self.pen_size = pen_size

    def press(self):
        self.model.tool = 'thickness' #if color button is selected, change mode to thickness, line buttons will appear
        # self.model.line_color = self.color
        self.model.pen_size = self.pen_size

class Color_Button(Button):
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def __init__(self,x,y,path,size,model,pen_size):
        super().__init__(x,y,path,size,model)
        self.pen_size = pen_size

    def press(self):
        self.model.tool = 'color_slider' #if color button is selected, change mode to thickness, line buttons will appear
        self.model.pen_size = self.pen_size

class Erase_Button(Button):
    """
    A class for adding an eraser button to the program.
    """
    def __init__(self,x,y,path,size,model,color,pen_size):
        super().__init__(x,y,path,size,model)
        self.pen_size = pen_size

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
    def press(self):
        self.model.tool = 'rectangle_1'

class Ellipse_Button(Button):
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
    def press(self):
        self.model.tool = 'draw'

class Color_Select_Button(Button):
    def press(self):
        self.model.tool = 'erase' #if eraser thickness button pressed, start erasing again
        self.model.eraser_size = self.eraser_size



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
                self.selected = Color_Choice
                self.pressed=True

            else:
                self.pressed = False
                # if not self.pressed:
                #     self.pressed = True
                # else: #Debounce
                #     self.pressed = False

    def display(self,frame):
        for i in range(self.dy):
            for j in range(self.dx):
                if self.icon[i,j][3] > 20:
                    frame[self.y+i,self.x+j] = self.icon[i,j][0:-1]
class Color_Choice():
    """
    A class for adding a color button to the program. Inherets from Button class.
    Color buttons change the color of the users drawing.
    """
    def __init__(self,x,y,size,model,color,pressed = False):
        self.x = x
        self.y = y
        self.size = size
        self.pressed = pressed
        self.model = model
        self.color = color #colorsys.hsv_to_rgb(color,255,50)

    def check_pressed(self,cursor):
        if cursor:
            if cursor[0] > self.x and cursor[0] < self.x + self.size and cursor[1] > self.y and cursor[1] < self.y + self.size:
                if not self.pressed:
                    self.press()
                    self.pressed = True
            else: #Debounce
                self.pressed = False

    def press(self):
        self.model.tool = 'draw' #if eraser thickness button pressed, start erasing again
        self.model.line_color = self.rgbcolor
        # self.model.line_color = "chosen_color"


    def update(self,color):
        self.color = color #colorsys.hsv_to_rgb(color,255,50)


    def display(self,frame):
        color = self.color
        #print("hsv",color)
        bgrcolor = [i * 255 for i in colorsys.hsv_to_rgb(color, 1, .50)]
        self.rgbcolor = (bgrcolor[2],bgrcolor[1],bgrcolor[0])
        #print("rgb",self.rgbcolor)
        cv2.rectangle(self.model.frame,(self.x,self.y),(self.x+self.size,self.y+self.size), self.rgbcolor,-1)

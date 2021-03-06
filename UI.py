import sys
from cv2 import cv2
from numpy.lib.function_base import select
from tools import Arena, distance_two_points
from PySide2 import QtWidgets
from PySide2 import QtGui
from PySide2 import QtCore
from PySide2.QtCore import QCoreApplication, QLine, QMutex, QRect, QSize, QWaitCondition
from PySide2.QtWidgets import QBoxLayout, QCheckBox, QComboBox, QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QWidget, QFileDialog
from PySide2.QtGui import QIcon


class rodentTracking(QWidget):
    #constants
    FILE_SELECTION = 0
    ARENA_DEFINITION = 1
    SCALE_DEFINITION = 2
    ARENA_DRAW = 3
    VIDEO = 4

    
    def __init__(self):
        super().__init__()
        self.width = 800
        self.height = 300
        self.setWindowTitle('Rodent Tracking')
        self.show()

        #file properties 
        self.video_file = ''
        self.config_file = ''
        self.use_saved_config = False

        #image properties
        self.image_frame = QLabel(self)

        #arenas properties
        self.number_of_arenas = 1 #defaults to 1
        self.arena_type = Arena.CIRCLE #defaults to circle
        self.arenas = []
        self.arena_points_number = 0

        
        
        #misc properties
        self.next = False
        self.current_screen = rodentTracking.FILE_SELECTION
        self.scale_points_number = 0
        self.real_world_scale = 1.0 #default
        self.scale_factor = 1
        

        #calling methods
        self.change_layout_file_selection()
        self.change_layout_arena_definitions()

        #loading a frame so the user can draw the arenas
        video = cv2.VideoCapture(self.video_file)
        frame_number = int(video.get(cv2.CAP_PROP_FRAME_COUNT)/2)
        video.set(1, frame_number)
        status, self.frame = video.read()
        video.release()
        #resize the image(some parameters will be properties to be used later)
        self.old_height, self.old_width, channels = self.frame.shape
        self.scale_factor = 500/self.old_height
        new_height = int(self.scale_factor * self.old_height)
        new_width = int(self.scale_factor * self.old_width)
        new_shape = (new_width, new_height)
        self.frame = cv2.resize(self.frame, new_shape, interpolation= cv2.INTER_AREA)
        self.change_layout_scale()
        for i in range(self.number_of_arenas):
            if(self.use_saved_config):
                break
            self.change_layout_add_new_arena()
        self.change_layout_video()
        
        
        

    #closeEvent override
    def closeEvent(self, event):
        exit()

    #mouse handler event override
    def mousePressEvent(self, event: QtGui.QMouseEvent):
        (x, y) = (event.x() - 10, event.y() - 10)
        if x < 0 or y < 0:
            return
        
        #transformations (these are necessary because the arenas are defined in relation to the original image)
        x = int(x/self.scale_factor)
        y = int(y/self.scale_factor)

        
        if self.current_screen == rodentTracking.ARENA_DRAW:
            if (self.arena_type == Arena.CIRCLE):
                self.new_point_circle(x, y)
            elif (self.arena_type == Arena.RECTANGLE):
                self.new_point_rectangle(x, y)
            elif (self.arena_type == Arena.FREE_FORM):
                self.new_point_free_form(x, y, event.button())

        elif self.current_screen == rodentTracking.SCALE_DEFINITION:
            self.new_point_scale(x, y)
        


    def new_point_scale(self, x, y):
        if self.scale_points_number == 0:
            self.scale_first_point = (x, y)
            self.scale_points_number += 1
        elif self.scale_points_number == 1:
            self.real_world_scale = distance_two_points((x, y), self.scale_first_point)
            self.scale_points_number += 1
            #draw
            first_point = (int(self.scale_first_point[0]*self.scale_factor),int(self.scale_first_point[1]*self.scale_factor))
            second_point = (int(x*self.scale_factor),int(y*self.scale_factor))
            cv2.line(self.frame, first_point, second_point, (255, 0, 0), 3)



    def new_point_circle(self, x, y):
        if (self.arena_points_number == 0):
            self.dictionary = {}
            self.dictionary['center'] = (x, y)
        elif (self.arena_points_number == 1):
            self.dictionary['radius'] = int(distance_two_points((x, y), self.dictionary['center']))
            self.arenas.append(Arena(Arena.CIRCLE, self.dictionary.copy()))
            #draw
            center = (int(self.dictionary['center'][0]*self.scale_factor),int(self.dictionary['center'][1]*self.scale_factor))
            radius = int(self.dictionary['radius']*self.scale_factor)
            cv2.circle(self.frame, center, radius, (0, 255, 0), 3)
        elif (self.arena_points_number >= 2):
            return
        
        self.arena_points_number += 1

    def new_point_rectangle(self, x, y):
        if (self.arena_points_number == 0):
            self.dictionary = {}
            self.dictionary['top_left'] = (x, y)
        elif (self.arena_points_number == 1):
            self.dictionary['bot_right'] = (x, y)
            self.arenas.append(Arena(Arena.RECTANGLE, self.dictionary.copy()))
            #draw
            top_left = (int(self.dictionary['top_left'][0]*self.scale_factor),int(self.dictionary['top_left'][1]*self.scale_factor))
            bot_right = (int(self.dictionary['bot_right'][0]*self.scale_factor),int(self.dictionary['bot_right'][1]*self.scale_factor))
            cv2.rectangle(self.frame, top_left, bot_right, (0, 255, 0), 3)
        elif (self.arena_points_number >= 2):
            return
        
        self.arena_points_number += 1

    def new_point_free_form(self, x, y, button):
        if self.arena_points_number == 0:
            self.dictionary = {}
            self.dictionary['points_list'] = []
            self.arena_points_number += 1
        if button == QtCore.Qt.LeftButton:
            self.dictionary['points_list'].append((x, y))
        elif button == QtCore.Qt.RightButton:
            self.arenas.append(Arena(Arena.FREE_FORM, self.dictionary))
            #draw
            points = []
            for p in self.dictionary['points_list']:
                points.append((int(p[0]*self.scale_factor), int(p[1]*self.scale_factor)))

            for i in range(len(points)):
                cv2.line(self.frame, points[i], points[(i+1)%len(points)], (0, 255, 0), 3)
        






    def get_video_file(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Select the video", "", "Videos (*.mp4)")
        self.text_video.setText(self.video_file)
    
    def get_cfg_file(self):
        if(self.checkbox_cfg.checkState()):
            self.config_file, _ = QFileDialog.getOpenFileName(self, "Select the configuration", "", "Configs (*.cfg)")

    def change_layout_video(self):
        self.current_screen = rodentTracking.VIDEO
        self.next = False
        self.width = 1280
        self.height = 720
        self.resize(self.width, self.height)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.move(0, 0)

    def change_layout_file_selection(self):
        self.next = False
        self.current_screen = rodentTracking.FILE_SELECTION
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.width = 800
        self.height = 300
        self.resize(self.width, self.height)

        self.layout.addSpacing(150)#mb put a logo of some sort later


        #video selection layout and widgets
        video_layout = QGridLayout()
        self.text_video = QLineEdit("No video selected")
        self.text_video.setReadOnly(True)

        button_video = QPushButton("...")
        button_video.setBaseSize(20, 20)
        button_video.clicked.connect(self.get_video_file)

        video_layout.addWidget(button_video, 0, 1, 1, 1)
        video_layout.addWidget(self.text_video, 0, 0, 1, 1)

        #cfg selection layout and widgets
        cfg_layout = QGridLayout()

        self.checkbox_cfg = QCheckBox("Use saved configuration?", self)
        self.checkbox_cfg.setCheckState(QtCore.Qt.Unchecked)#start unchecked

        self.text_cfg = QLineEdit("No cfg selected")
        self.text_cfg.setReadOnly(True)

        button_cfg = QPushButton("...")
        button_cfg.setBaseSize(20, 20)
        button_cfg.clicked.connect(self.get_cfg_file)

        cfg_layout.addWidget(self.checkbox_cfg, 0, 0, 1, 1)
        cfg_layout.addWidget(button_cfg, 1, 1, 1, 1)
        cfg_layout.addWidget(self.text_cfg, 1, 0, 1, 1)

        #next button
        next_layout = QBoxLayout(QBoxLayout.RightToLeft)

        button_next = QPushButton("Next")
        button_next.setFixedSize(80, 20)
        button_next.clicked.connect(self.next_button_handler)
        next_layout.addWidget(button_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)

        #add layouts to main layout
        
        self.layout.addLayout(video_layout)
        #self.layout.addLayout(cfg_layout)
        self.layout.addLayout(next_layout)

       
        

        self.setLayout(self.layout)
        self.show()

        #necessary to keep checking the events
        while not self.next:
            QCoreApplication.processEvents()

        QWidget().setLayout(self.layout)#free the layout


    def change_layout_arena_definitions(self):
        self.next = False
        self.current_screen = rodentTracking.ARENA_DEFINITION
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)

        #number of arenas and type of arena
        arenas_layout = QBoxLayout(QBoxLayout.TopToBottom)

        box_number_of_arenas = QSpinBox()
        box_number_of_arenas.setRange(1, 10)

        box_arena_type = QComboBox()
        box_arena_type.addItem("Circle")
        box_arena_type.addItem("Rectangle")
        box_arena_type.addItem("Free Form")
        

        arenas_layout.addWidget(box_arena_type)
        arenas_layout.addWidget(box_number_of_arenas)

        


        #next button
        next_layout = QBoxLayout(QBoxLayout.RightToLeft)

        button_next = QPushButton("Next")
        button_next.setFixedSize(80, 20)
        button_next.clicked.connect(self.next_button_handler)
        next_layout.addWidget(button_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)



        #add layouts to main layout
        self.layout.addLayout(arenas_layout)
        self.layout.addLayout(next_layout)


        self.setLayout(self.layout)
        self.show()

        #necessary to keep checking the events
        while not self.next:
            QCoreApplication.processEvents()
        
        self.number_of_arenas = box_number_of_arenas.value()
        self.arena_type = box_arena_type.currentIndex()


        QWidget().setLayout(self.layout)#free the layout

    def change_layout_add_new_arena(self):
        self.next = False
        self.current_screen = rodentTracking.ARENA_DRAW
        self.arena_points = []
        self.arena_points_number = 0
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        #next button
        next_layout = QBoxLayout(QBoxLayout.RightToLeft)

        button_next = QPushButton("Next")
        button_next.setFixedSize(80, 20)
        button_next.clicked.connect(self.next_button_handler)
        next_layout.addWidget(button_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)


        #adding layouts

        image_frame = QLabel(self)

        self.layout.addWidget(image_frame)
        self.layout.addLayout(next_layout)

        self.setLayout(self.layout)
        self.show()

        #necessary to keep checking the events
        while not self.next:
            self.show_cv2_img(self.frame, image_frame)
            QCoreApplication.processEvents()
        
        QWidget().setLayout(self.layout)#free the layout

    def change_layout_scale(self):
        self.current_screen = rodentTracking.SCALE_DEFINITION
        self.next = False
        self.arena_points = []
        self.arena_points_number = 0
        self.layout = QBoxLayout(QBoxLayout.TopToBottom)
        self.width = 800
        self.height = 600
        self.resize(self.width, self.height)

        #next button
        next_layout = QBoxLayout(QBoxLayout.RightToLeft)

        button_next = QPushButton("Next")
        button_next.setFixedSize(80, 20)
        button_next.clicked.connect(self.next_button_handler)
        next_layout.addWidget(button_next, alignment=QtCore.Qt.AlignRight | QtCore.Qt.AlignBottom)


        text_scale = QLineEdit("Distance in cm")
        text_scale.setReadOnly(False)

        next_layout.addWidget(text_scale, alignment=QtCore.Qt.AlignLeft | QtCore.Qt.AlignBottom)

        #adding layouts

        image_frame = QLabel(self)

        self.layout.addWidget(image_frame)
        self.layout.addLayout(next_layout)

        self.setLayout(self.layout)
        self.show()

        #necessary to keep checking the events
        while not self.next:
            self.show_cv2_img(self.frame, image_frame)
            QCoreApplication.processEvents()
        
        self.real_world_scale = (int(text_scale.text())/100)/self.real_world_scale
        QWidget().setLayout(self.layout)#free the layout
        

    def show_cv2_img(self, img, widget):
        self.image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_BGR888)
        widget.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def next_button_handler(self):
        self.next = True
import sys
from tools import Arena
from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication, QLine, QMutex, QRect, QSize, QWaitCondition
from PySide6.QtWidgets import QBoxLayout, QCheckBox, QComboBox, QGridLayout, QLabel, QLineEdit, QPushButton, QSpinBox, QWidget, QFileDialog
from PySide6.QtGui import QIcon


class rodent_tracking(QWidget):
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
        
        #misc properties
        self.next = False

        #calling methods
        self.change_layout_file_selection()
        self.change_layout_arena_definitions()
        self.change_layout_video()
        
        
        

    #closeEvent override
    def closeEvent(self, event):
        exit()

    def get_video_file(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Select the video", "", "Videos (*.mp4)")
        self.text_video.setText(self.video_file)
    
    def get_cfg_file(self):
        if(self.checkbox_cfg.checkState()):
            self.config_file, _ = QFileDialog.getOpenFileName(self, "Select the configuration", "", "Configs (*.cfg)")

    def change_layout_video(self):
        self.next = False
        print('teste')
        self.width = 1280
        self.height = 720
        self.resize(self.width, self.height)
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.move(0, 0)

    def change_layout_file_selection(self):
        self.next = False
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
        self.layout.addLayout(cfg_layout)
        self.layout.addLayout(next_layout)

       
        

        self.setLayout(self.layout)
        self.show()

        #necessary to keep checking the events
        while not self.next:
            QCoreApplication.processEvents()

        QWidget().setLayout(self.layout)#free the layout


    def change_layout_arena_definitions(self):
        self.next = False

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
        

    def show_cv2_img(self, img):
        self.image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_BGR888)
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def next_button_handler(self):
        self.next = True
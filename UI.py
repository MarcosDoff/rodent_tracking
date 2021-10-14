import sys
from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6 import QtCore
from PySide6.QtCore import QCoreApplication, QLine, QMutex, QRect, QSize, QWaitCondition
from PySide6.QtWidgets import QBoxLayout, QCheckBox, QGridLayout, QLabel, QLineEdit, QPushButton, QWidget, QFileDialog
from PySide6.QtGui import QIcon


class rodent_tracking(QWidget):
    def __init__(self):
        super().__init__()
        self.width = 1280
        self.height = 720
        self.setWindowTitle('Rodent Tracking')
        self.show()

        #file properties 
        self.video_file = ''
        self.config_file = ''
        self.use_saved_config = False

        #image properties
        self.image_frame = QLabel(self)
        
        #misc properties
        self.next = False

        #calling methods
        self.change_layout_file_selection()
        
        
        

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
        self.go_to_next_layout = False
        print('teste')
        self.width = 1280
        self.height = 720
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)
        self.move(0, 0)

    def change_layout_file_selection(self):
        self.go_to_next_layout = False
        self.layout = QtWidgets.QBoxLayout(QBoxLayout.TopToBottom)
        self.width = 800
        self.height = 600

        self.layout.addSpacing(300)


        #video selection layout and widgets
        video_layout = QtWidgets.QGridLayout()
        self.text_video = QLineEdit("No video selected")
        self.text_video.setReadOnly(True)

        button_video = QPushButton("...")
        button_video.setBaseSize(20, 20)
        button_video.clicked.connect(self.get_video_file)

        video_layout.addWidget(button_video, 0, 1, 1, 1)
        video_layout.addWidget(self.text_video, 0, 0, 1, 1)

        #cfg selection layout and widgets
        cfg_layout = QtWidgets.QGridLayout()

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
        next_layout = QtWidgets.QBoxLayout(QBoxLayout.RightToLeft)

        button_next = QPushButton("Next")
        button_next.setFixedSize(80, 20)
        button_next.clicked.connect(self.next_button_handler)
        next_layout.addWidget(button_next, alignment=QtCore.Qt.AlignRight)

        #add layouts to main layout
        
        self.layout.addLayout(video_layout)
        self.layout.addLayout(cfg_layout)
        self.layout.addLayout(next_layout)

       
        

        self.setLayout(self.layout)
        self.show()

        while not self.next:
            QCoreApplication.processEvents()

        QWidget().setLayout(self.layout)#free the layout

        self.change_layout_video()

        


        


    def show_cv2_img(self, img):
        self.image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_BGR888)
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

    def next_button_handler(self):
        self.next = True
import sys
from PySide6 import QtWidgets
from PySide6 import QtGui
from PySide6.QtWidgets import QLabel, QWidget, QFileDialog
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
        

        #calling methods
        self.get_files()
        self.change_layout_video()

    #closeEvent override
    def closeEvent(self, event):
        exit()

    def get_files(self):
        self.video_file, _ = QFileDialog.getOpenFileName(self, "Select the video", "", "Videos (*.mp4)")

        if(self.use_saved_config):
            self.config_file, _ = QFileDialog.getOpenFileName(self, "Select the configuration", "", "Configs (*.cfg)")

    def change_layout_video(self):
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.addWidget(self.image_frame)
        self.setLayout(self.layout)


    def show_cv2_img(self, img):
        self.image = QtGui.QImage(img.data, img.shape[1], img.shape[0], QtGui.QImage.Format_BGR888)
        self.image_frame.setPixmap(QtGui.QPixmap.fromImage(self.image))

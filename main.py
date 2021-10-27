from cv2 import cv2
import numpy as np
from math import sqrt
from math import pi
import pandas as pd
import os
from tools import Arena, Rodent, contour_center
import UI
from PySide6.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PySide6.QtGui import QIcon



if __name__ == '__main__':

    #start the app
    app = QApplication()

    window = UI.rodentTracking()

    #get video file
    video_file = window.video_file

    video = cv2.VideoCapture(video_file)

    if(not video.isOpened()):
        print("Problem opening file")
        exit()

    fps = video.get(cv2.CAP_PROP_FPS)
    status, previous_frame = video.read()


    rodent_number = window.number_of_arenas
    scale = window.real_world_scale
    #initialize rodent variables
    rodent_contours = [None] * rodent_number
    rodents = []
    arenas = window.arenas
    for i in range(rodent_number):
        rodents.append(Rodent(position_array=[], scale=scale, video_file=video_file))
    while True:
        status, current_frame = video.read()
        if (not status):
            print ("reached the end of the video")
            break
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        #gaussian blur for Otsu's Thresholding
        gray_frame = cv2.GaussianBlur(gray_frame, (5,5), 1)
        ret, bw_frame = cv2.threshold(gray_frame, 0, 255, cv2.THRESH_BINARY+cv2.THRESH_OTSU)
        #erosion and dilation to get rid of glares
        kernel_size = 7
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_frame = cv2.morphologyEx(bw_frame, cv2.MORPH_OPEN, kernel)
        #border detection
        border_image = cv2.Canny(eroded_frame, 0, 1)

        contours, hierarchy = cv2.findContours(border_image, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
        contours_image = current_frame.copy()

        

        # #the following lines are for test purposes only
        # arenas = []
        # dictionary = {}
        
        # dictionary['radius'] = 140
        # dictionary['center'] = (342,313)
        # arenas.append(Arena(Arena.CIRCLE, dictionary.copy()))

        # dictionary['radius'] = 140
        # dictionary['center'] = (698,313)
        # arenas.append(Arena(Arena.CIRCLE, dictionary.copy()))


        #findeing the rodent in each arena
        for arena in arenas:
            i = i + 1

            #the rodent is a contour, so we must find the contour that is inside the arena
            for cnt in contours:
                M = cv2.moments(cnt)
                if (not M['m00']==0.0):
                   if(arena.is_contour_inside(cnt)):
                        index = arenas.index(arena)
                        rodent_contours[index] = cnt
                        rodents[index].position_array.append(contour_center(cnt))
                        break
                        


        try:
            for rod in rodent_contours:
                cv2.drawContours(contours_image, rod, -1, (0, 0, 255), 2)
        except:
            print('nothing whithin the boundaries')
        for arena in arenas:
            arena.draw(contours_image)
        resized_image = cv2.resize(contours_image, (1280, 720), interpolation=cv2.INTER_AREA)
        
        #cv2.imshow('video', resized_image)
        window.show_cv2_img(resized_image, window.image_frame)
        #end of loop
        cv2.waitKey(20)

    #recording the information obtained
    if not os.path.exists("results"):
        os.mkdir("results")
    for rd in rodents:
        rd.id = rodents.index(rd)
        rd.calculate_stats()
        rd.generate_report()

    
    
from cv2 import cv2, imshow
import numpy as np
from math import sqrt
from math import pi
import pandas as pd
import os
from tools import Arena, Rodent, barycenter_contours, contour_center
import UI
from PySide2.QtWidgets import QApplication, QWidget, QInputDialog, QLineEdit, QFileDialog
from PySide2.QtGui import QIcon



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
    #video.set(1, int(fps*15))#skip 15s
    status, previous_frame = video.read()


    rodent_number = window.number_of_arenas
    scale = window.real_world_scale
    #initialize rodent variables
    rodent_centers = [None] * rodent_number
    rodents = []
    arenas = window.arenas
    for i in range(rodent_number):
        rodents.append(Rodent(position_array=[], scale=scale, video_file=video_file))


    fgbg = cv2.bgsegm.createBackgroundSubtractorMOG()

    while True:
        status, current_frame = video.read()
        if (not status):
            print ("reached the end of the video")
            break
        gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)
        #gaussian blur
        gray_frame = cv2.GaussianBlur(gray_frame, (5,5), 1)
        #cv2.imshow('before', gray_frame)

        #histogram equalization
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        gray_frame = clahe.apply(gray_frame)
        #cv2.imshow('after', gray_frame)

        #MOG
        bw_frame = fgbg.apply(gray_frame ,learningRate=0.001)
        #cv2.imshow('mask', bw_frame)

        #morphology operations
        
        kernel_size = 7
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_frame = cv2.morphologyEx(bw_frame, cv2.MORPH_OPEN, kernel)
        kernel_size = 20
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_frame = cv2.morphologyEx(bw_frame, cv2.MORPH_GRADIENT, kernel)
        
        kernel_size = 10
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_frame = cv2.morphologyEx(bw_frame, cv2.MORPH_CLOSE, kernel)
        

        kernel_size = 7
        kernel = np.ones((kernel_size, kernel_size), np.uint8)
        eroded_frame = cv2.morphologyEx(bw_frame, cv2.MORPH_OPEN, kernel)

        #cv2.imshow('er', eroded_frame)
        #border detection
        border_image = cv2.Canny(eroded_frame, 0, 1)


        contours, hierarchy = cv2.findContours(eroded_frame, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        contours_image = current_frame.copy()

    
        #findeing the rodent in each arena
        for arena in arenas:
            i = i + 1
            contours_inside_arena = []
            #the rodent is a contour, so we must find the contour that is inside the arena
            for cnt in contours:
                M = cv2.moments(cnt)
                if (not M['m00']==0.0):
                    if(arena.is_contour_inside(cnt)):
                        
                        contours_inside_arena.append(cnt)
            
            if contours_inside_arena: #checks if the list is empty
                index = arenas.index(arena)
                rodent_center = barycenter_contours(contours_inside_arena)
                rodent_centers[index] = rodent_center
                rodents[index].position_array.append(rodent_center)

                
                        


        try:
            for rod in rodent_centers:
                cv2.circle(contours_image, rod, 10, (0, 0, 255), 2)
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

    
    
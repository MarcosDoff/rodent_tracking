from cv2 import cv2
import numpy as np
from math import sqrt
from math import pi
import pandas as pd
import os
from tools import Arena, Rodent, contour_center

def print_mouse_coordinates(event, x, y, flags, param):
    if(event == cv2.EVENT_LBUTTONDOWN):
        print(str(x) + ',' + str(y))

#setting mouse callback function
cv2.namedWindow('video')
cv2.setMouseCallback('video', print_mouse_coordinates)
scale = 1.0 #default

if __name__ == '__main__':

    video = cv2.VideoCapture('videos/Campo_Aberto_h.264_MP4.mp4')

    if(not video.isOpened()):
        print("Problem opening file")
        exit()

    fps = video.get(cv2.CAP_PROP_FPS)
    print(fps)
    status, previous_frame = video.read()


    #test
    rodent_number = 2
    #initialize rodent variables
    rodent_contours = [None] * rodent_number
    rodents = []
    for i in range(rodent_number):
        rodents.append(Rodent(position_array=[], scale=scale))
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

        

        #the following lines are for test purposes only
        arenas = []
        dictionary = {}
        
        dictionary['radius'] = 140
        dictionary['center'] = (342,313)
        arenas.append(Arena(Arena.CIRCLE, dictionary.copy()))

        dictionary['radius'] = 140
        dictionary['center'] = (698,313)
        arenas.append(Arena(Arena.CIRCLE, dictionary.copy()))
        #calculating the centroids and the distance to the center
        for arena in arenas:
            i = i + 1

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
        cv2.imshow('video', contours_image)
        #end of loop
        cv2.waitKey(20)

    #recording the information obtained
    if not os.path.exists("results"):
        os.mkdir("results")
    for rd in rodents:
        rd.id = rodents.index(rd)
        rd.calculate_stats()
        rd.generate_report()

    
    
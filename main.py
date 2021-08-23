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

if __name__ == '__main__':

    video = cv2.VideoCapture('videos/Campo_Aberto_h.264_MP4.mp4')

    if(not video.isOpened()):
        print("Problem opening file")
        exit()

    fps = video.get(cv2.CAP_PROP_FPS)
    print(fps)
    status, previous_frame = video.read()
    print(video.get(cv2.CAP_PROP_FRAME_COUNT))


    #test
    rodent_number = 2
    #initialize rodent variables
    rodent_contours = [None] * rodent_number
    rodents = []
    for i in range(rodent_number):
        rodents.append(Rodent(position_array=[]))
    i = 0 #debug
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
        arenas.append(Arena((342,313), 140))
        arenas.append(Arena((698,313), 140))
        #calculating the centroids and the distance to the center
        for arena in arenas:
            for cnt in contours:
                M = cv2.moments(cnt)
                if (not M['m00']==0.0):
                    cx = int(M['m10']/M['m00'])
                    cy = int(M['m01']/M['m00'])
                    dist_center = sqrt((cx - arena.center[0])**2 + (cy - arena.center[1])**2)

                    ext_left = tuple(cnt[cnt[:, :, 0].argmin()][0])
                    ext_right = tuple(cnt[cnt[:, :, 0].argmax()][0])
                    ext_top = tuple(cnt[cnt[:, :, 1].argmin()][0])
                    ext_bot = tuple(cnt[cnt[:, :, 1].argmax()][0])
                    dist_left = sqrt((ext_left[0] - arena.center[0])**2 + (ext_left[1] - arena.center[1])**2)
                    dist_right = sqrt((ext_right[0] - arena.center[0])**2 + (ext_right[1] - arena.center[1])**2)
                    dist_top = sqrt((ext_top[0] - arena.center[0])**2 + (ext_top[1] - arena.center[1])**2)
                    dist_bot = sqrt((ext_bot[0] - arena.center[0])**2 + (ext_bot[1] - arena.center[1])**2)
                    
                    if(dist_left < arena.radius and dist_right < arena.radius and
                    dist_top < arena.radius and dist_bot < arena.radius):
                        index = arenas.index(arena)
                        rodent_contours[index] = cnt
                        rodents[index].position_array.append(contour_center(cnt))
                        i = i + 1 #debug


        try:
            for rod in rodent_contours:
                cv2.drawContours(contours_image, rod, -1, (0, 0, 255), 2)
        except:
            print('nothing whithin the boundaries')
        for arena in arenas:
            cv2.circle(contours_image, arena.center, arena.radius, (0, 255, 0), 3)
        cv2.imshow('video', contours_image)
        #cv2.imshow('video', border_image)#debug
        #end of loop
        cv2.waitKey(20)

    print(i) #debug
    #recording the information obtained
    if not os.path.exists("results"):
        os.mkdir("results")
        print("here!")
    for rd in rodents:
        if not os.path.exists("results/rodent_" + str(rodents.index(rd))):
            os.mkdir("results/rodent_" + str(rodents.index(rd)))
        open("results/rodent_" + str(rodents.index(rd)) + "/results.csv", 'w').close()#create the file
        pd.DataFrame(rd.position_array).to_csv("results/rodent_" + str(rodents.index(rd)) + "/results.csv", header=None, index=None)


    
    
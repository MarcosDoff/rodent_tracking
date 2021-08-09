from cv2 import cv2
import numpy as np
from math import sqrt
from math import pi

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

    while True:
        status, current_frame = video.read()
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
        #cv2.drawContours(contours_image, contours, -1, (0, 0, 255), 5)

        
        #the following lines are for test purposes only
        center_left = (342,313)
        arena_radius = 140
        min = 1000000
        #calculating the centroids and the distance to the center
        for cnt in contours:
            M = cv2.moments(cnt)
            if (not M['m00']==0.0):
                cx = int(M['m10']/M['m00'])
                cy = int(M['m01']/M['m00'])
                dist_center = sqrt((cx - center_left[0])**2 + (cy - center_left[1])**2)

                ext_left = tuple(cnt[cnt[:, :, 0].argmin()][0])
                dist_left = sqrt((ext_left[0] - center_left[0])**2 + (ext_left[1] - center_left[1])**2)
                if ((dist_center < min) and dist_left < arena_radius):
                    min = dist_center
                    rodent_contour = cnt
        try:
            cv2.drawContours(contours_image, rodent_contour, -1, (0, 0, 255), 5)
        except:
            print('nothing whithin the boundaries')
        cv2.circle(contours_image, center_left, arena_radius, (0, 255, 0), 5)
        cv2.imshow('video', contours_image)
        #cv2.imshow('video', border_image)#debug
        #end of loop
        cv2.waitKey(20)

        


    
    
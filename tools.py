from dataclasses import dataclass
from typing import List
from cv2 import cv2
from math import sqrt
from matplotlib import path
import pandas as pd
import numpy as np
import os

@dataclass
class Arena:
    #variables
    variant: int
    relevant_parameters: dict
    #constants
    CIRCLE = 0
    RECTANGLE = 1
    FREE_FORM = 2
    #methods
    def __init__(self, variant, relevant_parameters):#the logic that determines and records the parameters will be done in the main program
        self.variant = variant
        self.relevant_parameters = relevant_parameters
        #check if the parameters match the variant
        if self.variant == Arena.CIRCLE:
            if not ('center' in self.relevant_parameters.keys() and 'radius' in self.relevant_parameters.keys()):
                print('CIRCLE does not contain center or radius')
                exit()
        elif self.variant == Arena.RECTANGLE:
            if not ('bot_right' in self.relevant_parameters.keys() and 'top_left' in self.relevant_parameters.keys()):
                print('RECTANGLE does not contain bot_right or top_left')
                exit()

    def is_contour_inside(self, cnt,):
        ext_left = tuple(cnt[cnt[:, :, 0].argmin()][0])
        ext_right = tuple(cnt[cnt[:, :, 0].argmax()][0])
        ext_top = tuple(cnt[cnt[:, :, 1].argmin()][0])
        ext_bot = tuple(cnt[cnt[:, :, 1].argmax()][0])
                    
        if(self.is_point_inside(ext_left) and self.is_point_inside(ext_right) and self.is_point_inside(ext_top) and self.is_point_inside(ext_bot)):
            return True
        return False

    def is_point_inside(self, point):
        #determines whether a point is inside the arena or not
        #will have a different implementation depending on the variant
        if self.variant == Arena.CIRCLE:
            center = self.relevant_parameters['center']
            radius = self.relevant_parameters['radius']
            if distance_two_points(center, point) > radius:
                return False
            return True
        elif self.variant == Arena.RECTANGLE:
            bot_right = self.relevant_parameters['bot_right']
            top_left = self.relevant_parameters['top_left']
            if point[0] > top_left[0] and point[0] < bot_right[0] and point[1] < top_left[1] and point[1] >bot_right[1]:
                return True
            return False
        elif self.variant == Arena.FREE_FORM:
            poly = []
            for p in self.relevant_parameters['points_list']:
                poly.append(p)
            poly = path.Path(poly)
            return poly.contains_points([point])
               
        else:
            return False

    def draw(self, img):
        if self.variant == Arena.CIRCLE:
            cv2.circle(img, self.relevant_parameters['center'], self.relevant_parameters['radius'], (0, 255, 0), 3)
        elif self.variant == Arena.RECTANGLE:
            cv2.rectangle(img, self.relevant_parameters['top_left'], self.relevant_parameters['bot_right'], (0, 255, 0), 3)
        elif self.variant == Arena.FREE_FORM:
            points_list = self.relevant_parameters['points_list']
            for i in range(len(points_list)):
                cv2.line(img, points_list[i], points_list[(i+1)%len(points_list)], (0, 255, 0), 3)


@dataclass
class Rodent:
    position_array: List
    distance_between_frames_in_pixels: List
    distance_between_frames_in_meters: List
    sum_of_distances: float
    scale: float
    id: int

    def __init__(self, position_array, scale, video_file):
        self.position_array = position_array
        self.scale = scale
        self.distance_between_frames_in_pixels = [0]
        self.distance_between_frames_in_meters = []
        self.sum_of_distances = 0.0 #initialize as zero
        self.id = -1

        #split the video file
        video_file = os.path.splitext(video_file)[0]
        sections = video_file.split("/")
        self.video_file = sections.pop()
        

    def calculate_distance_between_frames(self):
        for i in range(1, len(self.position_array)):
            d = distance_two_points(self.position_array[i], self.position_array[i - 1])
            self.distance_between_frames_in_pixels.append(d)
    
    def calculate_distance_meters(self):
        for d in self.distance_between_frames_in_pixels:
            self.distance_between_frames_in_meters.append(self.scale * d)

    def calculate_total_traveled_distance(self):
        for d in self.distance_between_frames_in_meters:
            self.sum_of_distances += d

    def calculate_stats(self):
        self.calculate_distance_between_frames()
        self.calculate_distance_meters()
        self.calculate_total_traveled_distance()

    def generate_report(self):
        frame = [self.position_array, self.distance_between_frames_in_pixels,
        self.distance_between_frames_in_meters, [self.sum_of_distances]]
        data_frame = pd.DataFrame(data= frame).T
        user_folder = os.environ['USERPROFILE'].replace('\\','/')
        if not os.path.exists(user_folder+ "/Documents/RodentTracking/results/" + self.video_file + "/rodent_" + str(self.id)):
            os.makedirs(user_folder+ "/Documents/RodentTracking/results/" + self.video_file + "/rodent_" + str(self.id))
        open(user_folder+ "/Documents/RodentTracking/results/" + self.video_file + "/rodent_" + str(self.id) + "/results.csv", 'w').close()#create the file
        data_frame.to_csv(user_folder+ "/Documents/RodentTracking/results/" + self.video_file + "/rodent_" + str(self.id) + "/results.csv", index=None, sep=';',
        header=['Positions', 'Distance(pixels)', 'Distance(m)', 'Total Traveled Distance (m)'])


def contour_center(contour):
    moments = cv2.moments(contour)
    cX = int(moments["m10"] / moments["m00"])
    cY = int(moments["m01"] / moments["m00"])
    return (cX, cY)

#calculates the distance between two points (the points are tuples)
def distance_two_points(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

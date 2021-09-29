from dataclasses import dataclass
from typing import List
from cv2 import cv2
from math import sqrt
import pandas as pd
import os

@dataclass
class Arena:
    center: tuple
    radius: int

@dataclass
class Rodent:
    position_array: List
    distance_between_frames_in_pixels: List
    distance_between_frames_in_meters: List
    sum_of_distances: float
    scale: float
    id: int

    def __init__(self, position_array, scale):
        self.position_array = position_array
        self.scale = scale
        self.distance_between_frames_in_pixels = [0]
        self.distance_between_frames_in_meters = []
        self.sum_of_distances = 0.0 #initialize as zero
        self.id = -1

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
        if not os.path.exists("results/rodent_" + str(self.id)):
            os.mkdir("results/rodent_" + str(self.id))
        open("results/rodent_" + str(self.id) + "/results.csv", 'w').close()#create the file
        data_frame.to_csv("results/rodent_" + str(self.id) + "/results.csv", index=None, sep=';',
        header=['Positions', 'Distance(pixels)', 'Distance(m)', 'Total Traveled Distance'])


def contour_center(contour):
    moments = cv2.moments(contour)
    cX = int(moments["m10"] / moments["m00"])
    cY = int(moments["m01"] / moments["m00"])
    return (cX, cY)

#calculates the distance between two points (the points are tuples)
def distance_two_points(p1, p2):
    return sqrt((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2)

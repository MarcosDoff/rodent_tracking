from dataclasses import dataclass
from typing import List
from cv2 import cv2

@dataclass
class Arena:
    center: tuple
    radius: int

@dataclass
class Rodent:
    position_array: List

def contour_center(contour):
    moments = cv2.moments(contour)
    cX = int(moments["m10"] / moments["m00"])
    cY = int(moments["m01"] / moments["m00"])
    return (cX, cY)

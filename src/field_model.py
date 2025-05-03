import numpy as np
import math
from particle import Particle

class FieldModel:
    def __init__(self):
        self.line_points = [((0, 0), (144, 0)), ((144, 0), (144, 144)), ((144, 144), (0, 144)), ((0, 144), (0, 0))]

    def get_distance_to_obstacle(self, particle: Particle):
        p1 = (particle.get_state()[0], particle.get_state()[1])
        p2 = (particle.get_state()[0] + math.cos(particle.get_state()[2]), particle.get_state()[1] + math.sin(particle.get_state()[2]))

        min_length = None

        for line in self.line_points:
            p3 = line[0]
            p4 = line[1]


            if ((p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])) == 0: # Parallel lines no intersection
                continue

            t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / ((p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]))

            u = -1*((p1[0] - p2[0]) * (p1[1] - p3[1]) - (p1[1] - p2[1]) * (p1[0] - p3[0])) / ((p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0]))

            if (t >= 0 and 0 <= u and u <= 1):
                if (min_length is None or min_length > t):
                    min_length = t

        return min_length
    
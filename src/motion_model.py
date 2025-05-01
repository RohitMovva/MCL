import numpy as np
import math

class MotionModel:
    def __init__(self, dt):
        self.dt = dt

    def create_mock_readings(self, state):
        """
        Simulate sensor readings based on the current state
        Args:
            state (list): Current state of the robot [x, y, theta]
        Return [front_dist, left_dist, right_dist, back_dist, orientation]
        """

        # Simulate sensor readings with some noise
        # Mock raycast to walls, walls form square top left corner (0,0), bottom right corner (144,144)
        front_dist = math.sin(state[2])/(144-state[1]) + np.random.normal(0, 0.01)
        left_dist = math.cos(state[2])/(state[0]) + np.random.normal(0, 0.01)
        right_dist = math.cos(state[2])/(144-state[0]) + np.random.normal(0, 0.01)
        back_dist = math.sin(state[2])/(state[1]) + np.random.normal(0, 0.01)

        orientation = state[2] + np.random.normal(0, 0.01)

        return [front_dist, left_dist, right_dist, back_dist, orientation]
        
        
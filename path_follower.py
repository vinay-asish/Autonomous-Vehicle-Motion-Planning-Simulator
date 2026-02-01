"""
Path following controller using Pure Pursuit algorithm
Designed for Ackermann steering geometry
"""

import numpy as np
import config


class PurePursuitController:
    """Pure Pursuit path following for Ackermann steering"""
    
    def __init__(self, lookahead_distance=40):
        """
        Initialize Pure Pursuit controller
        
        Args:
            lookahead_distance: How far ahead to look on path (pixels)
        """
        self.lookahead_distance = lookahead_distance
        self.current_waypoint_index = 0
        self.path = []
        
    def set_path(self, path):
        """Set the path to follow"""
        self.path = path
        self.current_waypoint_index = 0
        
    def calculate_steering(self, car):
        """
        Calculate steering angle to follow path
        
        Args:
            car: Car object with position and angle
            
        Returns:
            Desired steering angle in degrees
        """
        if not self.path or len(self.path) == 0:
            return 0.0
        
        # Find lookahead point
        lookahead_point = self._get_lookahead_point(car)
        
        if lookahead_point is None:
            return 0.0
        
        # Calculate steering angle using Pure Pursuit
        # Transform lookahead point to car's coordinate frame
        dx = lookahead_point[0] - car.x
        dy = lookahead_point[1] - car.y
        
        # Rotate to car's frame
        car_angle_rad = np.radians(car.angle)
        local_x = dx * np.cos(-car_angle_rad) - dy * np.sin(-car_angle_rad)
        local_y = dx * np.sin(-car_angle_rad) + dy * np.cos(-car_angle_rad)
        
        # Pure Pursuit formula
        # Steering angle = atan(2 * wheelbase * sin(alpha) / lookahead_distance)
        # where alpha is angle to lookahead point
        
        alpha = np.arctan2(local_y, local_x)
        
        # Wheelbase from car
        wheelbase = car.wheelbase
        
        # Calculate steering angle
        steering_angle = np.arctan2(2 * wheelbase * np.sin(alpha), self.lookahead_distance)
        
        # Convert to degrees and clamp
        steering_angle_deg = np.degrees(steering_angle)
        steering_angle_deg = np.clip(steering_angle_deg, -config.CAR_MAX_STEERING, config.CAR_MAX_STEERING)
        
        return steering_angle_deg
    
    def calculate_speed(self, car, target_speed=None):
        """
        Calculate desired speed based on path curvature
        
        Args:
            car: Car object
            target_speed: Maximum desired speed (default: CAR_MAX_SPEED)
            
        Returns:
            Desired speed
        """
        if target_speed is None:
            target_speed = config.CAR_MAX_SPEED
        
        # Slow down for sharp turns
        steering_angle = self.calculate_steering(car)
        
        # Reduce speed based on steering angle
        angle_factor = 1.0 - (abs(steering_angle) / config.CAR_MAX_STEERING) * 0.5
        
        # Slow down when near end of path
        if self.is_path_complete(car):
            distance_to_goal = self._distance(car.x, car.y, self.path[-1][0], self.path[-1][1])
            if distance_to_goal < 100:
                return target_speed * min(0.5, distance_to_goal / 100)
        
        return target_speed * angle_factor
    
    def _get_lookahead_point(self, car):
        """Find point on path at lookahead distance"""
        if not self.path:
            return None
        
        # Start from current waypoint
        for i in range(self.current_waypoint_index, len(self.path)):
            waypoint = self.path[i]
            dist = self._distance(car.x, car.y, waypoint[0], waypoint[1])
            
            if dist >= self.lookahead_distance:
                self.current_waypoint_index = max(0, i - 1)
                return waypoint
        
        # If no point found, return last point
        return self.path[-1]
    
    def is_path_complete(self, car, threshold=50):
        """Check if car has reached end of path"""
        if not self.path:
            return True
        
        goal = self.path[-1]
        dist = self._distance(car.x, car.y, goal[0], goal[1])
        return dist < threshold
    
    def _distance(self, x1, y1, x2, y2):
        """Euclidean distance"""
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def get_progress(self, car):
        """Get progress along path (0.0 to 1.0)"""
        if not self.path or len(self.path) <= 1:
            return 1.0
        
        return self.current_waypoint_index / (len(self.path) - 1)
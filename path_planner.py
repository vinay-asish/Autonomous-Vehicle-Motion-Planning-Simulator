"""
Path planning using RRT (Rapidly-exploring Random Tree)
"""

import numpy as np
import random
from scipy.interpolate import splprep, splev
import config


class Node:
    """Node in the RRT tree"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.parent = None
        self.cost = 0.0


class RRTPlanner:
    """RRT path planner for obstacle avoidance"""
    
    def __init__(self, environment):
        self.environment = environment
        self.nodes = []
        self.path = []
        
        # # RRT parameters
        # self.max_iterations = 3000
        # self.step_size = 30  # Distance to extend tree
        # self.goal_sample_rate = 0.15  # 15% chance to sample goal
        # self.goal_threshold = 40  # Distance to consider goal reached

        # RRT parameters - adjusted for denser environments
        self.max_iterations = config.RRT_MAX_ITERATIONS if hasattr(config, 'RRT_MAX_ITERATIONS') else 5000
        self.step_size = config.RRT_STEP_SIZE if hasattr(config, 'RRT_STEP_SIZE') else 25
        self.goal_sample_rate = config.RRT_GOAL_SAMPLE_RATE if hasattr(config, 'RRT_GOAL_SAMPLE_RATE') else 0.20
        self.goal_threshold = 35  # Smaller threshold for smaller goal

        self.visualization_callback = None
        self.visualization_interval = 5

    def set_visualization_callback(self, callback):
        """Set callback function for visualization updates"""
        self.visualization_callback = callback
        
    # def plan(self, start_x, start_y, goal_x, goal_y):
    #     """
    #     Plan a path from start to goal
        
    #     Args:
    #         start_x, start_y: Starting position
    #         goal_x, goal_y: Goal position
            
    #     Returns:
    #         List of (x, y) waypoints, or None if no path found
    #     """
    #     # Initialize tree with start node
    #     start_node = Node(start_x, start_y)
    #     self.nodes = [start_node]
        
    #     print(f"Planning path from ({start_x:.0f}, {start_y:.0f}) to ({goal_x:.0f}, {goal_y:.0f})")
        
    #     for i in range(self.max_iterations):
    #         # Sample random point (or goal)
    #         if random.random() < self.goal_sample_rate:
    #             rand_x, rand_y = goal_x, goal_y
    #         else:
    #             rand_x = random.uniform(0, self.environment.width)
    #             rand_y = random.uniform(0, self.environment.height)
            
    #         # Find nearest node in tree
    #         nearest_node = self._get_nearest_node(rand_x, rand_y)
            
    #         # Extend tree towards random point
    #         new_node = self._extend_tree(nearest_node, rand_x, rand_y)
            
    #         if new_node is None:
    #             continue  # Extension failed (collision)
            
    #         # Add new node to tree
    #         self.nodes.append(new_node)
            
    #         # Check if goal is reached
    #         dist_to_goal = self._distance(new_node.x, new_node.y, goal_x, goal_y)
    #         if dist_to_goal < self.goal_threshold:
    #             print(f"Path found! Iterations: {i+1}, Nodes: {len(self.nodes)}")
    #             # Extract path
    #             path = self._extract_path(new_node)
    #             # Add goal as final point
    #             path.append((goal_x, goal_y))
    #             return path
        
    #     print(f"No path found after {self.max_iterations} iterations")
    #     return None

    def plan(self, start_x, start_y, goal_x, goal_y):
        """
        Plan a path from start to goal with visualization
        
        Args:
            start_x, start_y: Starting position
            goal_x, goal_y: Goal position
            
        Returns:
            List of (x, y) waypoints, or None if no path found
        """
        # Initialize tree with start node
        start_node = Node(start_x, start_y)
        self.nodes = [start_node]
        
        print(f"Planning path from ({start_x:.0f}, {start_y:.0f}) to ({goal_x:.0f}, {goal_y:.0f})")
        
        for i in range(self.max_iterations):
            # Sample random point (or goal)
            if random.random() < self.goal_sample_rate:
                rand_x, rand_y = goal_x, goal_y
            else:
                rand_x = random.uniform(0, self.environment.width)
                rand_y = random.uniform(0, self.environment.height)
            
            # Find nearest node in tree
            nearest_node = self._get_nearest_node(rand_x, rand_y)
            
            # Extend tree towards random point
            new_node = self._extend_tree(nearest_node, rand_x, rand_y)
            
            if new_node is None:
                continue
            
            # Add new node to tree
            self.nodes.append(new_node)
            
            # Visualization update - NEW
            if self.visualization_callback and (i % self.visualization_interval == 0):
                self.visualization_callback({
                    'iteration': i,
                    'nodes': self.nodes,
                    'new_node': new_node,
                    'random_point': (rand_x, rand_y),
                    'goal': (goal_x, goal_y)
                })
            
            # Check if goal is reached
            dist_to_goal = self._distance(new_node.x, new_node.y, goal_x, goal_y)
            if dist_to_goal < self.goal_threshold:
                print(f"Path found! Iterations: {i+1}, Nodes: {len(self.nodes)}")
                
                # Final visualization update - NEW
                if self.visualization_callback:
                    self.visualization_callback({
                        'iteration': i,
                        'nodes': self.nodes,
                        'new_node': new_node,
                        'goal_reached': True,
                        'goal': (goal_x, goal_y)
                    })
                
                # Extract path
                path = self._extract_path(new_node)
                path.append((goal_x, goal_y))
                return path
        
        print(f"No path found after {self.max_iterations} iterations")
        return None
    
    def _get_nearest_node(self, x, y):
        """Find nearest node in tree to given point"""
        min_dist = float('inf')
        nearest = None
        
        for node in self.nodes:
            dist = self._distance(node.x, node.y, x, y)
            if dist < min_dist:
                min_dist = dist
                nearest = node
        
        return nearest
    
    def _extend_tree(self, from_node, to_x, to_y):
        """Extend tree from node towards point"""
        # Calculate direction
        dx = to_x - from_node.x
        dy = to_y - from_node.y
        dist = np.sqrt(dx**2 + dy**2)
        
        if dist == 0:
            return None
        
        # Normalize and scale by step size
        step_x = (dx / dist) * min(self.step_size, dist)
        step_y = (dy / dist) * min(self.step_size, dist)
        
        new_x = from_node.x + step_x
        new_y = from_node.y + step_y
        
        # Check if path to new point is collision-free
        if not self._is_path_clear(from_node.x, from_node.y, new_x, new_y):
            return None
        
        # Create new node
        new_node = Node(new_x, new_y)
        new_node.parent = from_node
        new_node.cost = from_node.cost + self._distance(from_node.x, from_node.y, new_x, new_y)
        
        return new_node
    
    def _is_path_clear(self, x1, y1, x2, y2, num_checks=10):
        """Check if straight line path is collision-free"""
        for i in range(num_checks + 1):
            t = i / num_checks
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            
            # Check collision at this point (using a car-sized radius)
            car_radius = max(config.CAR_WIDTH, config.CAR_LENGTH) / 2+5
            
            # Check boundaries
            if x < car_radius or x > self.environment.width - car_radius:
                return False
            if y < car_radius or y > self.environment.height - car_radius:
                return False
            
            # Check obstacles
            for obstacle in self.environment.obstacles:
                if hasattr(obstacle, 'contains_point'):
                    # Expand obstacle check by car radius
                    if self._point_near_obstacle(x, y, obstacle, car_radius):
                        return False
        
        return True
    
    def _point_near_obstacle(self, x, y, obstacle, radius):
        """Check if point is within radius of obstacle"""
        if hasattr(obstacle, 'radius'):  # Circle obstacle
            dist = np.sqrt((x - obstacle.x)**2 + (y - obstacle.y)**2)
            return dist < (obstacle.radius + radius)
        else:  # Rectangle obstacle
            # Check if point is within expanded rectangle
            expanded_x = obstacle.x - radius
            expanded_y = obstacle.y - radius
            expanded_width = obstacle.width + 2 * radius
            expanded_height = obstacle.height + 2 * radius
            
            return (expanded_x <= x <= expanded_x + expanded_width and
                    expanded_y <= y <= expanded_y + expanded_height)
    
    def _extract_path(self, goal_node):
        """Extract path from goal back to start"""
        path = []
        current = goal_node
        
        while current is not None:
            path.append((current.x, current.y))
            current = current.parent
        
        # Reverse to get start-to-goal order
        path.reverse()
        return path
    
    def _distance(self, x1, y1, x2, y2):
        """Euclidean distance"""
        return np.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    
    def smooth_path(self, path, smoothness=0.0):
        """
        Smooth path using B-splines
        
        Args:
            path: List of (x, y) waypoints
            smoothness: Smoothing factor (0 = no smoothing, higher = more smooth)
            
        Returns:
            List of smoothed (x, y) points
        """
        if len(path) < 3:
            return path
        
        # Extract x and y coordinates
        path_array = np.array(path)
        x = path_array[:, 0]
        y = path_array[:, 1]
        
        # Fit B-spline
        try:
            # k=3 for cubic spline, s for smoothness
            tck, u = splprep([x, y], s=smoothness, k=min(3, len(path)-1))
            
            # Evaluate spline at more points for smooth curve
            u_new = np.linspace(0, 1, len(path) * 5)
            x_new, y_new = splev(u_new, tck)
            
            # Return as list of tuples
            smooth_path = list(zip(x_new, y_new))
            
            print(f"Path smoothed: {len(path)} waypoints -> {len(smooth_path)} points")
            return smooth_path
            
        except Exception as e:
            print(f"Smoothing failed: {e}, using original path")
            return path
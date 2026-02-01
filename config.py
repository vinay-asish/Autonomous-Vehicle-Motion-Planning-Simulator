"""
Configuration file for motion planning simulation
"""

# Window settings
WINDOW_WIDTH = 1500
WINDOW_HEIGHT = 900
FPS = 60

# Visual effects
ENABLE_SHADOWS = True
ENABLE_PARTICLES = True  # Tire marks, dust
ENABLE_GLOW = True
ENABLE_SMOOTH_GRAPHICS = True  # Anti-aliasing

# Colors (R, G, B)
# Background - realistic asphalt road
COLOR_BACKGROUND = (45, 52, 54)  # Dark asphalt
COLOR_ROAD_LINES = (241, 196, 15)  # Yellow road markings
COLOR_GRASS = (39, 174, 96)  # Grass/off-road

# Car colors - modern car appearance
COLOR_CAR_BODY = (41, 128, 185)  # Deep blue
COLOR_CAR_WINDOW = (52, 73, 94)  # Dark gray windows
COLOR_CAR_WHEEL = (44, 62, 80)  # Dark wheels
COLOR_CAR_LIGHT = (255, 235, 59)  # Headlights

# Obstacle colors - realistic buildings/barriers
COLOR_OBSTACLE_BUILDING = (149, 165, 166)  # Gray concrete
COLOR_OBSTACLE_DANGER = (192, 57, 43)  # Red danger zones
COLOR_OBSTACLE_WALL = (127, 140, 141)  # Wall color

COLOR_GOAL = (46, 204, 113)  # Green
COLOR_GRID = (60, 70, 73)  # Subtle grid
COLOR_TEXT = (236, 240, 241)  # Light text
COLOR_UI_BACKGROUND = (30, 30, 30)  # Dark UI panels

# Car properties
CAR_WIDTH = 20
CAR_LENGTH = 35
CAR_MAX_SPEED = 2.5  # pixels per frame
CAR_ACCELERATION = 0.2
CAR_DECELERATION = 0.6
CAR_MAX_STEERING = 45  # degrees
CAR_STEERING_SPEED = 3  # degrees per frame

# Initial car position
CAR_START_X = 70
CAR_START_Y = 70
CAR_START_ANGLE = 0  # degrees

# Obstacle properties - varied types
OBSTACLE_TYPES = {
    'building': COLOR_OBSTACLE_BUILDING,
    'danger': COLOR_OBSTACLE_DANGER,
    'wall': COLOR_OBSTACLE_WALL
}
OBSTACLE_BORDER_WIDTH = 3

# Grid settings
SHOW_GRID = True
GRID_SIZE = 50
GRID_STYLE = 'road'  # 'road' or 'grid'

# Goal settings
GOAL_RADIUS = 20

# Shadow settings
SHADOW_OFFSET = 5
SHADOW_COLOR = (0, 0, 0)
SHADOW_ALPHA = 80  # Transparency (0-255)

# Particle system (tire marks)
MAX_PARTICLES = 200
PARTICLE_FADE_RATE = 3
PARTICLE_SIZE = 3

# RRT Planning parameters (for denser environments)
RRT_MAX_ITERATIONS = 5000  # More iterations for complex paths
RRT_STEP_SIZE = 25  # Smaller steps for tight spaces
RRT_GOAL_SAMPLE_RATE = 0.20  # Higher rate to reach goal faster

# Camera settings
CAMERA_FOLLOW = False  # Set to True for car-following camera
CAMERA_SMOOTHNESS = 0.1

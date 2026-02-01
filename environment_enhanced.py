"""
Enhanced Environment with realistic visual effects
"""

import pygame
import numpy as np
import config


class Obstacle:
    """Enhanced rectangular obstacle with textures and 3D effect"""
    def __init__(self, x, y, width, height, obstacle_type='building'):
        """
        Create an enhanced obstacle
        
        Args:
            x, y: Top-left corner position
            width, height: Obstacle dimensions
            obstacle_type: 'building', 'danger', or 'wall'
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.obstacle_type = obstacle_type
        self.color = config.OBSTACLE_TYPES.get(obstacle_type, config.COLOR_OBSTACLE_BUILDING)
        
    def draw(self, screen):
        """Draw the obstacle with 3D effect and texture"""
        rect = pygame.Rect(self.x, self.y, self.width, self.height)
        
        # Draw shadow
        if config.ENABLE_SHADOWS:
            shadow_rect = rect.copy()
            shadow_rect.x += config.SHADOW_OFFSET
            shadow_rect.y += config.SHADOW_OFFSET
            shadow_surf = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
            shadow_color = (*config.SHADOW_COLOR, config.SHADOW_ALPHA)
            pygame.draw.rect(shadow_surf, shadow_color, (0, 0, self.width, self.height))
            screen.blit(shadow_surf, (shadow_rect.x, shadow_rect.y))
        
        # Draw main body
        pygame.draw.rect(screen, self.color, rect)
        
        # Add texture/pattern based on type
        if self.obstacle_type == 'building':
            self._draw_building_texture(screen, rect)
        elif self.obstacle_type == 'danger':
            self._draw_danger_pattern(screen, rect)
        
        # Draw 3D edge highlight
        highlight_color = tuple(min(255, c + 30) for c in self.color)
        pygame.draw.line(screen, highlight_color, 
                        (rect.left, rect.top), (rect.right, rect.top), 2)
        pygame.draw.line(screen, highlight_color, 
                        (rect.left, rect.top), (rect.left, rect.bottom), 2)
        
        # Draw shadow edge
        shadow_edge_color = tuple(max(0, c - 30) for c in self.color)
        pygame.draw.line(screen, shadow_edge_color, 
                        (rect.right, rect.top), (rect.right, rect.bottom), 2)
        pygame.draw.line(screen, shadow_edge_color, 
                        (rect.left, rect.bottom), (rect.right, rect.bottom), 2)
        
        # Draw border
        pygame.draw.rect(screen, (0, 0, 0), rect, config.OBSTACLE_BORDER_WIDTH)
        
    def _draw_building_texture(self, screen, rect):
        """Draw window pattern for building obstacles"""
        window_size = 12
        window_gap = 18
        window_color = (70, 50, 40)
        
        for x in range(rect.left + 10, rect.right - 10, window_gap):
            for y in range(rect.top + 10, rect.bottom - 10, window_gap):
                window_rect = pygame.Rect(x, y, window_size, window_size)
                pygame.draw.rect(screen, window_color, window_rect)
                pygame.draw.rect(screen, (50, 30, 70), window_rect, 1)
                
    def _draw_danger_pattern(self, screen, rect):
        """Draw warning stripes for danger zones"""
        stripe_width = 20
        stripe_color1 = self.color
        stripe_color2 = (241, 196, 15)  # Yellow
        
        x = rect.left
        use_color1 = True
        while x < rect.right:
            stripe_rect = pygame.Rect(x, rect.top, min(stripe_width, rect.right - x), rect.height)
            color = stripe_color1 if use_color1 else stripe_color2
            pygame.draw.rect(screen, color, stripe_rect)
            x += stripe_width
            use_color1 = not use_color1
        
    def get_corners(self):
        """Get obstacle corners for collision detection"""
        return [
            (self.x, self.y),
            (self.x + self.width, self.y),
            (self.x + self.width, self.y + self.height),
            (self.x, self.y + self.height)
        ]
        
    def contains_point(self, x, y):
        """Check if a point is inside the obstacle"""
        return (self.x <= x <= self.x + self.width and 
                self.y <= y <= self.y + self.height)


class CircleObstacle:
    """Enhanced circular obstacle"""
    def __init__(self, x, y, radius, obstacle_type='wall'):
        """
        Create an enhanced circular obstacle
        
        Args:
            x, y: Center position
            radius: Obstacle radius
            obstacle_type: Type of obstacle
        """
        self.x = x
        self.y = y
        self.radius = radius
        self.obstacle_type = obstacle_type
        self.color = config.OBSTACLE_TYPES.get(obstacle_type, config.COLOR_OBSTACLE_WALL)
        
    def draw(self, screen):
        """Draw the obstacle with gradient effect"""
        # Draw shadow
        if config.ENABLE_SHADOWS:
            shadow_surf = pygame.Surface((int(self.radius * 2.5), int(self.radius * 2.5)), pygame.SRCALPHA)
            shadow_color = (*config.SHADOW_COLOR, config.SHADOW_ALPHA)
            pygame.draw.circle(shadow_surf, shadow_color, 
                             (int(self.radius * 1.25), int(self.radius * 1.25)), 
                             int(self.radius))
            screen.blit(shadow_surf, (self.x - self.radius * 1.25 + config.SHADOW_OFFSET, 
                                     self.y - self.radius * 1.25 + config.SHADOW_OFFSET))
        
        # Draw gradient circles (3D effect)
        for i in range(3):
            radius = self.radius - (i * 2)
            if radius > 0:
                shade = int(30 * i / 3)
                color = tuple(min(255, c + shade) for c in self.color)
                pygame.draw.circle(screen, color, (int(self.x), int(self.y)), int(radius))
        
        # Draw border
        pygame.draw.circle(screen, (0, 0, 0), (int(self.x), int(self.y)), 
                         int(self.radius), config.OBSTACLE_BORDER_WIDTH)
        
    def contains_point(self, x, y):
        """Check if a point is inside the obstacle"""
        distance = np.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.radius


class Goal:
    """Enhanced goal with animated effects"""
    def __init__(self, x, y, radius=None):
        """
        Create an enhanced goal location
        
        Args:
            x, y: Goal position
            radius: Goal radius (default from config)
        """
        self.x = x
        self.y = y
        self.radius = radius if radius else config.GOAL_RADIUS
        self.color = config.COLOR_GOAL
        self.reached = False
        self.pulse = 0  # For pulsing animation
        
    def update(self):
        """Update goal animation"""
        self.pulse = (self.pulse + 0.1) % (2 * np.pi)
        
    def draw(self, screen):
        """Draw the goal with pulsing animation"""
        # Pulsing effect
        pulse_offset = int(5 * np.sin(self.pulse))
        current_radius = self.radius + pulse_offset
        
        # Draw glow if enabled
        if config.ENABLE_GLOW:
            for i in range(3, 0, -1):
                glow_radius = current_radius + (i * 8)
                alpha = 40 // i
                glow_surf = pygame.Surface((glow_radius * 2, glow_radius * 2), pygame.SRCALPHA)
                glow_color = (*self.color, alpha)
                pygame.draw.circle(glow_surf, glow_color, (glow_radius, glow_radius), glow_radius)
                screen.blit(glow_surf, (self.x - glow_radius, self.y - glow_radius))
        
        # Draw main circle
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), int(current_radius))
        
        # Draw inner circles
        inner_color = tuple(min(255, c + 50) for c in self.color)
        pygame.draw.circle(screen, inner_color, (int(self.x), int(self.y)), 
                         int(current_radius * 0.7))
        
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                         int(current_radius * 0.4))
        
        # Draw border
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 
                         int(current_radius), 3)
        
        # Draw "GOAL" text
        if self.radius > 25:
            font = pygame.font.Font(None, 24)
            text = font.render("GOAL", True, (255, 255, 255))
            text_rect = text.get_rect(center=(int(self.x), int(self.y)))
            screen.blit(text, text_rect)
            
    def is_reached(self, x, y):
        """Check if position (x, y) has reached the goal"""
        distance = np.sqrt((x - self.x)**2 + (y - self.y)**2)
        return distance <= self.radius


class Environment:
    """Enhanced environment with realistic graphics"""
    def __init__(self, width, height):
        """
        Create enhanced environment
        
        Args:
            width, height: Environment dimensions
        """
        self.width = width
        self.height = height
        self.obstacles = []
        self.goal = None
        
        # Create default scenario with varied obstacles
        self.create_enhanced_scenario()
        
    # def create_enhanced_scenario(self):
    #     """Create a visually interesting scenario"""
    #     # Buildings
    #     self.obstacles.append(Obstacle(300, 200, 120, 220, 'building'))
    #     self.obstacles.append(Obstacle(650, 50, 180, 140, 'building'))
    #     self.obstacles.append(Obstacle(950, 300, 140, 200, 'building'))
        
    #     # Danger zones
    #     self.obstacles.append(Obstacle(500, 500, 220, 50, 'danger'))
    #     self.obstacles.append(Obstacle(200, 650, 180, 40, 'danger'))
        
    #     # Walls
    #     self.obstacles.append(Obstacle(50, 400, 120, 50, 'wall'))
    #     self.obstacles.append(Obstacle(850, 650, 50, 120, 'wall'))
        
    #     # Circular obstacles
    #     self.obstacles.append(CircleObstacle(480, 350, 65, 'wall'))
    #     self.obstacles.append(CircleObstacle(800, 550, 55, 'building'))
    #     self.obstacles.append(CircleObstacle(1150, 450, 50, 'danger'))
        
    #     # Set goal
    #     self.goal = Goal(1250, 750)
    # def create_enhanced_scenario(self):
    #     """Create a challenging scenario with many small obstacles"""
        
    #     # === BUILDINGS (Gray) - Medium sized obstacles ===
    #     # Left side buildings
    #     self.obstacles.append(Obstacle(200, 150, 50, 30, 'building'))
    #     self.obstacles.append(Obstacle(200, 300, 50, 30, 'building'))
    #     self.obstacles.append(Obstacle(200, 480, 50, 30, 'building'))
    #     self.obstacles.append(Obstacle(200, 620, 50, 70, 'building'))
    #     self.obstacles.append(Obstacle(200, 780, 50, 70, 'building'))
        
    #     # Center-left buildings
    #     self.obstacles.append(Obstacle(400, 50, 40, 70, 'building'))
    #     self.obstacles.append(Obstacle(400, 280, 40, 70, 'building'))
    #     self.obstacles.append(Obstacle(400, 440, 40, 70, 'building'))
    #     self.obstacles.append(Obstacle(400, 590, 40, 70, 'building'))
    #     self.obstacles.append(Obstacle(400, 760, 40, 70, 'building'))
        
    #     # Center buildings
    #     self.obstacles.append(Obstacle(620, 150, 50, 70, 'building'))
    #     self.obstacles.append(Obstacle(620, 340, 50, 80, 'building'))
    #     self.obstacles.append(Obstacle(620, 500, 50, 30, 'building'))
    #     self.obstacles.append(Obstacle(620, 680, 50, 70, 'building'))
        
    #     # Center-right buildings
    #     self.obstacles.append(Obstacle(850, 50, 40, 120, 'building'))
    #     self.obstacles.append(Obstacle(850, 270, 40, 50, 'building'))
    #     self.obstacles.append(Obstacle(850, 420, 40, 140, 'building'))
    #     self.obstacles.append(Obstacle(850, 610, 40, 110, 'building'))
    #     self.obstacles.append(Obstacle(850, 770, 40, 50, 'building'))
        
    #     # Right side buildings
    #     self.obstacles.append(Obstacle(1070, 150, 50, 130, 'building'))
    #     self.obstacles.append(Obstacle(1070, 330, 50, 50, 'building'))
    #     self.obstacles.append(Obstacle(1070, 480, 50, 120, 'building'))
    #     self.obstacles.append(Obstacle(1070, 650, 50, 110, 'building'))
        
    #     # Far right buildings
    #     self.obstacles.append(Obstacle(1280, 200, 70, 50, 'building'))
    #     self.obstacles.append(Obstacle(1280, 350, 70, 120, 'building'))
    #     self.obstacles.append(Obstacle(1280, 520, 70, 110, 'building'))
    #     self.obstacles.append(Obstacle(1280, 680, 70, 50, 'building'))
        
    #     # === DANGER ZONES (Red/Yellow stripes) - Small obstacles ===
    #     # Scattered danger zones creating tight passages
    #     self.obstacles.append(Obstacle(320, 200, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(520, 150, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(320, 420, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(520, 380, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(740, 200, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(740, 420, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(970, 250, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(970, 500, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(1180, 300, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(1180, 550, 30, 30, 'danger'))
        
    #     # Bottom danger zones
    #     self.obstacles.append(Obstacle(320, 680, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(520, 720, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(740, 650, 30, 30, 'danger'))
    #     self.obstacles.append(Obstacle(970, 700, 30, 30, 'danger'))
        
    #     # === WALLS (Dark gray) - Small rectangular barriers ===
    #     # Create maze-like passages
    #     self.obstacles.append(Obstacle(300, 50, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(510, 50, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(740, 50, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(950, 50, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(1160, 50, 50, 40, 'wall'))
        
    #     self.obstacles.append(Obstacle(300, 560, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(510, 560, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(740, 560, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(950, 560, 50, 40, 'wall'))
    #     self.obstacles.append(Obstacle(1160, 560, 50, 40, 'wall'))
        
    #     # === CIRCULAR OBSTACLES (Mixed types) ===
    #     # Small circular obstacles creating additional complexity
    #     self.obstacles.append(CircleObstacle(350, 250, 35, 'wall'))
    #     self.obstacles.append(CircleObstacle(550, 220, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(780, 280, 35, 'wall'))
    #     self.obstacles.append(CircleObstacle(1000, 180, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(1220, 240, 35, 'wall'))
        
    #     self.obstacles.append(CircleObstacle(350, 470, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(550, 510, 35, 'wall'))
    #     self.obstacles.append(CircleObstacle(780, 450, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(1000, 540, 35, 'wall'))
    #     self.obstacles.append(CircleObstacle(1220, 480, 30, 'building'))
        
    #     self.obstacles.append(CircleObstacle(350, 720, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(550, 650, 35, 'building'))
    #     self.obstacles.append(CircleObstacle(780, 730, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(1000, 650, 35, 'building'))
    #     self.obstacles.append(CircleObstacle(1220, 720, 30, 'wall'))
        
    #     # Additional small circular obstacles for extra challenge
    #     self.obstacles.append(CircleObstacle(460, 340, 25, 'danger'))
    #     self.obstacles.append(CircleObstacle(680, 360, 25, 'danger'))
    #     self.obstacles.append(CircleObstacle(910, 380, 25, 'danger'))
    #     self.obstacles.append(CircleObstacle(1130, 400, 25, 'danger'))
        
    #     # === GOAL (Far right, challenging to reach) ===
    #     self.goal = Goal(1480, 850)
        
    #     print(f"Created challenging environment with {len(self.obstacles)} obstacles")

    # def create_enhanced_scenario(self):
    #     """Create a challenging scenario with many small obstacles - scaled for any window size"""
        
    #     # Calculate scaling factors based on window size
    #     w = self.width
    #     h = self.height
        
    #     # === BUILDINGS (Gray) - Medium sized obstacles ===
    #     # Left side buildings
    #     self.obstacles.append(Obstacle(150, 100, 70, 90, 'building'))
    #     self.obstacles.append(Obstacle(150, 220, 70, 100, 'building'))
    #     self.obstacles.append(Obstacle(150, 350, 70, 80, 'building'))
    #     self.obstacles.append(Obstacle(150, 460, 70, 90, 'building'))
    #     self.obstacles.append(Obstacle(150, 580, 70, 90, 'building'))
        
    #     # Center-left buildings
    #     self.obstacles.append(Obstacle(300, 80, 80, 110, 'building'))
    #     self.obstacles.append(Obstacle(300, 220, 80, 90, 'building'))
    #     self.obstacles.append(Obstacle(300, 340, 80, 85, 'building'))
    #     self.obstacles.append(Obstacle(300, 455, 80, 100, 'building'))
    #     self.obstacles.append(Obstacle(300, 585, 80, 95, 'building'))
        
    #     # Center buildings
    #     self.obstacles.append(Obstacle(480, 100, 90, 120, 'building'))
    #     self.obstacles.append(Obstacle(480, 250, 90, 95, 'building'))
    #     self.obstacles.append(Obstacle(480, 375, 90, 110, 'building'))
    #     self.obstacles.append(Obstacle(480, 515, 90, 100, 'building'))
        
    #     # Center-right buildings
    #     self.obstacles.append(Obstacle(660, 80, 80, 100, 'building'))
    #     self.obstacles.append(Obstacle(660, 210, 80, 85, 'building'))
    #     self.obstacles.append(Obstacle(660, 325, 80, 115, 'building'))
    #     self.obstacles.append(Obstacle(660, 470, 80, 95, 'building'))
    #     self.obstacles.append(Obstacle(660, 595, 80, 85, 'building'))
        
    #     # Right side buildings
    #     self.obstacles.append(Obstacle(830, 100, 70, 110, 'building'))
    #     self.obstacles.append(Obstacle(830, 240, 70, 85, 'building'))
    #     self.obstacles.append(Obstacle(830, 355, 70, 100, 'building'))
    #     self.obstacles.append(Obstacle(830, 485, 70, 95, 'building'))
        
    #     # Far right buildings
    #     self.obstacles.append(Obstacle(1000, 130, 60, 85, 'building'))
    #     self.obstacles.append(Obstacle(1000, 245, 60, 100, 'building'))
    #     self.obstacles.append(Obstacle(1000, 375, 60, 90, 'building'))
    #     self.obstacles.append(Obstacle(1000, 495, 60, 85, 'building'))
        
    #     # === DANGER ZONES (Red/Yellow stripes) - Small obstacles ===
    #     self.obstacles.append(Obstacle(240, 150, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(400, 120, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(240, 320, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(400, 295, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(580, 155, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(580, 325, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(750, 195, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(750, 385, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(920, 220, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(920, 415, 50, 50, 'danger'))
        
    #     # Bottom danger zones
    #     self.obstacles.append(Obstacle(240, 520, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(400, 545, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(580, 495, 50, 50, 'danger'))
    #     self.obstacles.append(Obstacle(750, 530, 50, 50, 'danger'))
        
    #     # === WALLS (Dark gray) - Small rectangular barriers ===
    #     self.obstacles.append(Obstacle(230, 60, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(390, 60, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(570, 60, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(740, 60, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(910, 60, 45, 35, 'wall'))
        
    #     self.obstacles.append(Obstacle(230, 425, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(390, 425, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(570, 425, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(740, 425, 45, 35, 'wall'))
    #     self.obstacles.append(Obstacle(910, 425, 45, 35, 'wall'))
        
    #     # === CIRCULAR OBSTACLES ===
    #     self.obstacles.append(CircleObstacle(270, 190, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(430, 170, 25, 'building'))
    #     self.obstacles.append(CircleObstacle(610, 215, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(780, 140, 25, 'building'))
    #     self.obstacles.append(CircleObstacle(950, 180, 30, 'wall'))
        
    #     self.obstacles.append(CircleObstacle(270, 360, 25, 'building'))
    #     self.obstacles.append(CircleObstacle(430, 390, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(610, 345, 25, 'building'))
    #     self.obstacles.append(CircleObstacle(780, 410, 30, 'wall'))
    #     self.obstacles.append(CircleObstacle(950, 370, 25, 'building'))
        
    #     self.obstacles.append(CircleObstacle(270, 545, 25, 'wall'))
    #     self.obstacles.append(CircleObstacle(430, 495, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(610, 555, 25, 'wall'))
    #     self.obstacles.append(CircleObstacle(780, 495, 30, 'building'))
    #     self.obstacles.append(CircleObstacle(950, 540, 25, 'wall'))
        
    #     # Additional small obstacles
    #     self.obstacles.append(CircleObstacle(355, 260, 20, 'danger'))
    #     self.obstacles.append(CircleObstacle(530, 280, 20, 'danger'))
    #     self.obstacles.append(CircleObstacle(710, 300, 20, 'danger'))
    #     self.obstacles.append(CircleObstacle(880, 320, 20, 'danger'))
        
    #     # === GOAL (Far right, challenging to reach) ===
    #     self.goal = Goal(w - 100, h - 50)
        
    #     print(f"Created challenging environment with {len(self.obstacles)} obstacles")

    def create_enhanced_scenario(self):
        """Create a challenging but solvable scenario - optimized for 1500x900"""
        
        # === LEFT COLUMN - Buildings (x: 150-250) ===
        self.obstacles.append(Obstacle(150, 120, 50, 70, 'building'))
        self.obstacles.append(Obstacle(150, 280, 50, 60, 'building'))
        # self.obstacles.append(Obstacle(150, 450, 50, 75, 'building'))
        self.obstacles.append(Obstacle(150, 610, 50, 70, 'building'))
        self.obstacles.append(Obstacle(150, 770, 50, 60, 'building'))
        
        # === COLUMN 2 - Mixed obstacles (x: 320-420) ===
        self.obstacles.append(Obstacle(320, 80, 55, 70, 'building'))
        self.obstacles.append(Obstacle(320, 260, 55, 80, 'building'))
        self.obstacles.append(Obstacle(320, 420, 55, 70, 'building'))
        # self.obstacles.append(Obstacle(320, 570, 55, 80, 'building'))
        self.obstacles.append(Obstacle(320, 740, 55, 90, 'building'))
        
        # Circular obstacles in column 2 gaps
        self.obstacles.append(CircleObstacle(357, 160, 28, 'wall'))
        self.obstacles.append(CircleObstacle(357, 300, 28, 'wall'))
        
        # === COLUMN 3 - Buildings (x: 500-590) ===
        self.obstacles.append(Obstacle(500, 100, 60, 80, 'building'))
        self.obstacles.append(Obstacle(500, 290, 60, 75, 'building'))
        # self.obstacles.append(Obstacle(500, 455, 60, 85, 'building'))
        self.obstacles.append(Obstacle(500, 630, 60, 70, 'building'))
        
        # Danger zones in column 3 gaps
        self.obstacles.append(Obstacle(515, 240, 60, 40, 'danger'))
        # self.obstacles.append(Obstacle(515, 405, 60, 40, 'danger'))
        self.obstacles.append(Obstacle(515, 580, 60, 40, 'danger'))
        self.obstacles.append(Obstacle(515, 740, 60, 40, 'danger'))
        
        # === COLUMN 4 - Mixed (x: 690-780) ===
        self.obstacles.append(Obstacle(690, 70, 85, 115, 'building'))
        self.obstacles.append(Obstacle(690, 245, 85, 100, 'building'))
        self.obstacles.append(Obstacle(690, 405, 85, 120, 'building'))
        # self.obstacles.append(Obstacle(690, 585, 85, 95, 'building'))
        self.obstacles.append(Obstacle(690, 740, 85, 110, 'building'))
        
        # Small walls creating narrow passages
        self.obstacles.append(Obstacle(700, 195, 50, 40, 'wall'))
        # self.obstacles.append(Obstacle(700, 355, 50, 40, 'wall'))
        self.obstacles.append(Obstacle(700, 535, 50, 40, 'wall'))
        
        # === COLUMN 5 - Buildings (x: 870-960) ===
        self.obstacles.append(Obstacle(870, 90, 70, 125, 'building'))
        self.obstacles.append(Obstacle(870, 275, 70, 105, 'building'))
        self.obstacles.append(Obstacle(870, 440, 70, 115, 'building'))
        self.obstacles.append(Obstacle(870, 615, 70, 100, 'building'))
        
        # Circular obstacles
        self.obstacles.append(CircleObstacle(915, 225, 30, 'building'))
        self.obstacles.append(CircleObstacle(915, 395, 30, 'building'))
        self.obstacles.append(CircleObstacle(915, 570, 30, 'building'))
        self.obstacles.append(CircleObstacle(915, 725, 30, 'building'))
        
        # === COLUMN 6 - Mixed (x: 1050-1140) ===
        self.obstacles.append(Obstacle(1050, 100, 65, 80, 'building'))
        self.obstacles.append(Obstacle(1050, 270, 65, 90, 'building'))
        self.obstacles.append(Obstacle(1050, 430, 65, 95, 'building'))
        # self.obstacles.append(Obstacle(1050, 595, 65, 80, 'building'))
        self.obstacles.append(Obstacle(1050, 765, 65, 95, 'building'))
        
        # Danger zones
        self.obstacles.append(Obstacle(1065, 220, 35, 30, 'danger'))
        self.obstacles.append(Obstacle(1065, 380, 35, 30, 'danger'))
        # self.obstacles.append(Obstacle(1065, 545, 35, 30, 'danger'))
        self.obstacles.append(Obstacle(1065, 715, 35, 30, 'danger'))
        
        # === COLUMN 7 - Buildings (x: 1230-1315) ===
        self.obstacles.append(Obstacle(1230, 110, 60, 95, 'building'))
        self.obstacles.append(Obstacle(1230, 285, 60, 95, 'building'))
        # self.obstacles.append(Obstacle(1230, 440, 60, 90, 'building'))
        self.obstacles.append(Obstacle(1230, 610, 60, 80, 'building'))
        
        # Small circular obstacles for variety
        self.obstacles.append(CircleObstacle(1270, 235, 25, 'wall'))
        # self.obstacles.append(CircleObstacle(1270, 395, 25, 'wall'))
        self.obstacles.append(CircleObstacle(1270, 565, 25, 'wall'))
        self.obstacles.append(CircleObstacle(1270, 720, 25, 'wall'))
        
        # === SCATTERED OBSTACLES (for additional challenge) ===
        # Top horizontal line of small obstacles
        self.obstacles.append(Obstacle(250, 50, 45, 35, 'wall'))
        self.obstacles.append(Obstacle(430, 50, 45, 35, 'wall'))
        self.obstacles.append(Obstacle(620, 50, 45, 35, 'wall'))
        # self.obstacles.append(Obstacle(810, 50, 45, 35, 'wall'))
        self.obstacles.append(Obstacle(990, 50, 45, 35, 'wall'))
        self.obstacles.append(Obstacle(1170, 50, 45, 35, 'wall'))
        
        # Middle scattered circular obstacles (creating interesting paths)
        self.obstacles.append(CircleObstacle(270, 450, 25, 'danger'))
        self.obstacles.append(CircleObstacle(445, 300, 28, 'danger'))
        # self.obstacles.append(CircleObstacle(630, 520, 25, 'danger'))
        self.obstacles.append(CircleObstacle(815, 350, 28, 'danger'))
        # self.obstacles.append(CircleObstacle(995, 480, 25, 'danger'))
        self.obstacles.append(CircleObstacle(1175, 340, 28, 'danger'))
        
        # Bottom horizontal line
        self.obstacles.append(Obstacle(250, 860, 45, 30, 'wall'))
        # self.obstacles.append(Obstacle(430, 860, 45, 30, 'wall'))
        self.obstacles.append(Obstacle(620, 860, 45, 30, 'wall'))
        # self.obstacles.append(Obstacle(810, 860, 45, 30, 'wall'))
        self.obstacles.append(Obstacle(990, 860, 45, 30, 'wall'))
        
        # === GOAL (Bottom right corner, accessible) ===
        self.goal = Goal(1420, 830)
        
        print(f"Created well-spread environment with {len(self.obstacles)} obstacles")
        print(f"Environment size: {self.width}x{self.height}")
        
    def update(self):
        """Update environment animations"""
        if self.goal:
            self.goal.update()
        
    def add_obstacle(self, obstacle):
        """Add an obstacle to the environment"""
        self.obstacles.append(obstacle)
        
    def set_goal(self, x, y):
        """Set goal location"""
        self.goal = Goal(x, y)
        
    def check_collision(self, car):
        """Check if car collides with any obstacle or boundary"""
        # Check boundary collision
        if (car.x < 20 or car.x > self.width - 20 or 
            car.y < 20 or car.y > self.height - 20):
            return True
            
        car_corners = car.get_corners()
        
        for obstacle in self.obstacles:
            if isinstance(obstacle, Obstacle):
                if self._polygon_collision(car_corners, obstacle.get_corners()):
                    return True
            elif isinstance(obstacle, CircleObstacle):
                if self._circle_polygon_collision(obstacle, car_corners):
                    return True
                    
        return False
        
    def _polygon_collision(self, poly1, poly2):
        """Check collision between two convex polygons"""
        for point in poly1:
            if self._point_in_polygon(point, poly2):
                return True
        for point in poly2:
            if self._point_in_polygon(point, poly1):
                return True
        return False
        
    def _point_in_polygon(self, point, polygon):
        """Check if a point is inside a polygon using ray casting"""
        x, y = point
        n = len(polygon)
        inside = False
        
        p1x, p1y = polygon[0]
        for i in range(1, n + 1):
            p2x, p2y = polygon[i % n]
            if y > min(p1y, p2y):
                if y <= max(p1y, p2y):
                    if x <= max(p1x, p2x):
                        if p1y != p2y:
                            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                        if p1x == p2x or x <= xinters:
                            inside = not inside
            p1x, p1y = p2x, p2y
            
        return inside
        
    def _circle_polygon_collision(self, circle, polygon):
        """Check collision between circle and polygon"""
        if self._point_in_polygon((circle.x, circle.y), polygon):
            return True
            
        for point in polygon:
            distance = np.sqrt((point[0] - circle.x)**2 + (point[1] - circle.y)**2)
            if distance <= circle.radius:
                return True
                
        for i in range(len(polygon)):
            p1 = polygon[i]
            p2 = polygon[(i + 1) % len(polygon)]
            if self._circle_line_collision(circle, p1, p2):
                return True
                
        return False
        
    def _circle_line_collision(self, circle, p1, p2):
        """Check if circle collides with line segment"""
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        fx = circle.x - p1[0]
        fy = circle.y - p1[1]
        
        if dx == 0 and dy == 0:
            distance = np.sqrt(fx**2 + fy**2)
            return distance <= circle.radius
            
        t = max(0, min(1, (fx * dx + fy * dy) / (dx * dx + dy * dy)))
        closest_x = p1[0] + t * dx
        closest_y = p1[1] + t * dy
        distance = np.sqrt((circle.x - closest_x)**2 + (circle.y - closest_y)**2)
        
        return distance <= circle.radius
        
    def check_goal_reached(self, car):
        """Check if car has reached the goal"""
        if self.goal:
            return self.goal.is_reached(car.x, car.y)
        return False
        
    def draw(self, screen):
        """Draw all environment elements with enhanced graphics"""
        # Draw road/grid
        if config.SHOW_GRID:
            if config.GRID_STYLE == 'road':
                self._draw_road_markings(screen)
            else:
                self._draw_grid(screen)
            
        # Draw obstacles
        for obstacle in self.obstacles:
            obstacle.draw(screen)
            
        # Draw goal
        if self.goal:
            self.goal.draw(screen)
            
    def _draw_road_markings(self, screen):
        """Draw road-style markings"""
        line_color = config.COLOR_ROAD_LINES
        line_length = 40
        line_gap = 30
        
        # Horizontal road lines
        for y in range(config.GRID_SIZE, self.height, config.GRID_SIZE * 2):
            x = 0
            while x < self.width:
                pygame.draw.line(screen, line_color, 
                               (x, y), (min(x + line_length, self.width), y), 2)
                x += line_length + line_gap
                
        # Vertical road lines
        for x in range(config.GRID_SIZE, self.width, config.GRID_SIZE * 2):
            y = 0
            while y < self.height:
                pygame.draw.line(screen, line_color, 
                               (x, y), (x, min(y + line_length, self.height)), 2)
                y += line_length + line_gap
                
    def _draw_grid(self, screen):
        """Draw background grid"""
        grid_color = config.COLOR_GRID
        
        for x in range(0, self.width, config.GRID_SIZE):
            pygame.draw.line(screen, grid_color, (x, 0), (x, self.height), 1)
            
        for y in range(0, self.height, config.GRID_SIZE):
            pygame.draw.line(screen, grid_color, (0, y), (self.width, y), 1)

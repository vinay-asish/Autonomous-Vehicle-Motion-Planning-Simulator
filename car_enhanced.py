import pygame
import numpy as np
import config


class Particle:
    """Particle for tire marks and effects"""
    def __init__(self, x, y, color=(60, 60, 60)):
        self.x = x
        self.y = y
        self.color = color
        self.alpha = 255
        self.size = config.PARTICLE_SIZE
        
    def update(self):
        """Fade out particle"""
        self.alpha = max(0, self.alpha - config.PARTICLE_FADE_RATE)
        
    def is_alive(self):
        """Check if particle should still be rendered"""
        return self.alpha > 0
        
    def draw(self, surface):
        """Draw particle with transparency"""
        if self.alpha > 0:
            # Create surface with per-pixel alpha
            particle_surf = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
            color_with_alpha = (*self.color, int(self.alpha))
            pygame.draw.circle(particle_surf, color_with_alpha, 
                             (self.size, self.size), self.size)
            surface.blit(particle_surf, (self.x - self.size, self.y - self.size))


class Car:
    def __init__(self, x, y, angle=0):
        """
        Initialize enhanced car with visual effects
        
        Args:
            x: Initial x position
            y: Initial y position
            angle: Initial angle in degrees (0 = pointing right)
        """
        self.x = x
        self.y = y
        self.angle = angle  # degrees
        self.velocity = 0.0  # current speed
        self.steering_angle = 0.0  # current steering angle in degrees
        
        # Car dimensions
        self.width = config.CAR_WIDTH
        self.length = config.CAR_LENGTH
        
        # Physics parameters
        # self.max_speed = config.CAR_MAX_SPEED
        # self.acceleration = config.CAR_ACCELERATION
        # self.deceleration = config.CAR_DECELERATION
        # self.max_steering = config.CAR_MAX_STEERING
        # self.steering_speed = config.CAR_STEERING_SPEED

        # Physics parameters
        self.max_speed = config.CAR_MAX_SPEED
        self.acceleration = config.CAR_ACCELERATION
        self.deceleration = config.CAR_DECELERATION
        self.max_steering = config.CAR_MAX_STEERING
        self.steering_speed = config.CAR_STEERING_SPEED

        # Ackermann steering parameters
        self.wheelbase = self.length * 0.7  # Distance between front and rear axle
        self.track_width = self.width * 0.9  # Distance between left and right wheels

        # Wheel velocities for differential drive
        self.left_wheel_velocity = 0.0
        self.right_wheel_velocity = 0.0
        
        # Visual colors
        self.color_body = config.COLOR_CAR_BODY
        self.color_window = config.COLOR_CAR_WINDOW
        self.color_wheel = config.COLOR_CAR_WHEEL
        self.color_light = config.COLOR_CAR_LIGHT
        
        # Particle system for tire marks
        self.particles = []
        self.particle_timer = 0
        
    # def update(self, dt=1.0):
    #     """
    #     Update car position based on bicycle kinematic model
        
    #     Args:
    #         dt: Time step (default 1.0 for frame-based)
    #     """
    #     if abs(self.velocity) > 0.1:
    #         # Bicycle model kinematics
    #         wheelbase = self.length * 0.7
            
    #         # Convert angles to radians
    #         theta = np.radians(self.angle)
    #         delta = np.radians(self.steering_angle)
            
    #         # Calculate angular velocity
    #         angular_velocity = (self.velocity / wheelbase) * np.tan(delta)
            
    #         # Update position
    #         self.x += self.velocity * np.cos(theta) * dt
    #         self.y += self.velocity * np.sin(theta) * dt
            
    #         # Update angle
    #         self.angle += np.degrees(angular_velocity) * dt
            
    #         # Normalize angle to [-180, 180]
    #         self.angle = (self.angle + 180) % 360 - 180
            
    #         # Add tire marks if moving and turning
    #         if config.ENABLE_PARTICLES and abs(self.velocity) > 2 and abs(self.steering_angle) > 10:
    #             self.add_tire_mark()
                
    #     # Update particles
    #     if config.ENABLE_PARTICLES:
    #         for particle in self.particles[:]:
    #             particle.update()
    #             if not particle.is_alive():
    #                 self.particles.remove(particle)

    def update(self, dt=1.0):
        """
        Update car position using Ackermann steering with differential drive
        
        Args:
            dt: Time step (default 1.0 for frame-based)
        """
        if abs(self.velocity) > 0.1:
            # Convert steering angle to radians
            delta = np.radians(self.steering_angle)
            theta = np.radians(self.angle)
            
            # Ackermann steering geometry
            # Calculate the turning radius
            if abs(delta) > 0.001:  # Avoid division by zero
                # Turning radius at the center of the rear axle
                turning_radius = self.wheelbase / np.tan(delta)
                
                # Calculate inner and outer turning radii
                # Inner wheel (tighter turn)
                inner_radius = turning_radius - (self.track_width / 2)
                # Outer wheel (wider turn)
                outer_radius = turning_radius + (self.track_width / 2)
                
                # Differential drive: different wheel speeds
                if turning_radius > 0:  # Turning left
                    self.left_wheel_velocity = self.velocity * (inner_radius / turning_radius)
                    self.right_wheel_velocity = self.velocity * (outer_radius / turning_radius)
                else:  # Turning right
                    self.left_wheel_velocity = self.velocity * (outer_radius / abs(turning_radius))
                    self.right_wheel_velocity = self.velocity * (inner_radius / abs(turning_radius))
                
                # Angular velocity based on Ackermann geometry
                angular_velocity = self.velocity / turning_radius
                
            else:
                # Going straight - both wheels same speed
                self.left_wheel_velocity = self.velocity
                self.right_wheel_velocity = self.velocity
                angular_velocity = 0
            
            # Update position using the center velocity
            self.x += self.velocity * np.cos(theta) * dt
            self.y += self.velocity * np.sin(theta) * dt
            
            # Update angle
            self.angle += np.degrees(angular_velocity) * dt
            
            # Normalize angle to [-180, 180]
            self.angle = (self.angle + 180) % 360 - 180
            
            # Add tire marks if moving and turning
            if config.ENABLE_PARTICLES and abs(self.velocity) > 2 and abs(self.steering_angle) > 10:
                self.add_tire_mark()
                
        else:
            # Stationary - no wheel movement
            self.left_wheel_velocity = 0.0
            self.right_wheel_velocity = 0.0
            
        # Update particles
        if config.ENABLE_PARTICLES:
            for particle in self.particles[:]:
                particle.update()
                if not particle.is_alive():
                    self.particles.remove(particle)    
                    
    def add_tire_mark(self):
        """Add tire mark particles"""
        self.particle_timer += 1
        if self.particle_timer >= 3:  # Add particle every 3 frames
            self.particle_timer = 0
            
            # Get rear wheel positions
            corners = self.get_corners()
            rear_left = corners[0]
            rear_right = corners[1]
            
            # Add particles at rear wheels
            self.particles.append(Particle(rear_left[0], rear_left[1]))
            self.particles.append(Particle(rear_right[0], rear_right[1]))
            
            # Limit particle count
            if len(self.particles) > config.MAX_PARTICLES:
                self.particles.pop(0)
                
    def accelerate(self):
        """Increase car speed"""
        self.velocity = min(self.velocity + self.acceleration, self.max_speed)
        
    def brake(self):
        """Decrease car speed"""
        if self.velocity > 0:
            self.velocity = max(self.velocity - self.deceleration, 0)
        elif self.velocity < 0:
            self.velocity = min(self.velocity + self.deceleration, 0)
            
    def reverse(self):
        """Move car in reverse"""
        self.velocity = max(self.velocity - self.acceleration, -self.max_speed * 0.5)
        
    def steer_left(self):
        """Turn steering wheel left"""
        self.steering_angle = min(self.steering_angle + self.steering_speed, self.max_steering)
        
    def steer_right(self):
        """Turn steering wheel right"""
        self.steering_angle = max(self.steering_angle - self.steering_speed, -self.max_steering)
        
    def center_steering(self):
        """Return steering wheel to center"""
        if abs(self.steering_angle) < self.steering_speed:
            self.steering_angle = 0
        elif self.steering_angle > 0:
            self.steering_angle -= self.steering_speed
        else:
            self.steering_angle += self.steering_speed
            
    def get_corners(self):
        """Get the four corners of the car for collision detection"""
        half_length = self.length / 2
        half_width = self.width / 2
        
        corners_local = [
            (-half_length, -half_width),  # Rear left
            (-half_length, half_width),   # Rear right
            (half_length, half_width),    # Front right
            (half_length, -half_width),   # Front left
        ]
        
        theta = np.radians(self.angle)
        cos_theta = np.cos(theta)
        sin_theta = np.sin(theta)
        
        corners_world = []
        for lx, ly in corners_local:
            wx = lx * cos_theta - ly * sin_theta
            wy = lx * sin_theta + ly * cos_theta
            wx += self.x
            wy += self.y
            corners_world.append((wx, wy))
            
        return corners_world
        
    def draw_shadow(self, screen):
        """Draw car shadow for depth effect"""
        if not config.ENABLE_SHADOWS:
            return
            
        # Shadow offset
        shadow_offset = config.SHADOW_OFFSET
        
        # Get shadow corners (offset from car)
        corners = self.get_corners()
        shadow_corners = [(x + shadow_offset, y + shadow_offset) for x, y in corners]
        
        # Create shadow surface with alpha
        shadow_surface = pygame.Surface((config.WINDOW_WIDTH, config.WINDOW_HEIGHT), pygame.SRCALPHA)
        shadow_color = (*config.SHADOW_COLOR, config.SHADOW_ALPHA)
        pygame.draw.polygon(shadow_surface, shadow_color, shadow_corners)
        
        # Blit shadow
        screen.blit(shadow_surface, (0, 0))
        
    def draw(self, screen):
        """Draw the car with enhanced graphics"""
        # Draw particles (tire marks) first
        if config.ENABLE_PARTICLES:
            for particle in self.particles:
                particle.draw(screen)
        
        # Draw shadow
        self.draw_shadow(screen)
        
        # Get car corners
        corners = self.get_corners()
        
        # Draw car body (main)
        pygame.draw.polygon(screen, self.color_body, corners)
        
        # Draw car body outline (3D effect)
        outline_color = tuple(max(0, c - 40) for c in self.color_body)
        pygame.draw.polygon(screen, outline_color, corners, 3)
        
        # Draw windows (windshield and rear window)
        # Front windshield
        front_center = ((corners[2][0] + corners[3][0]) / 2, (corners[2][1] + corners[3][1]) / 2)
        mid_left = ((corners[3][0] + corners[0][0]) / 2, (corners[3][1] + corners[0][1]) / 2)
        mid_right = ((corners[2][0] + corners[1][0]) / 2, (corners[2][1] + corners[1][1]) / 2)
        
        window_points = [
            (front_center[0] * 0.7 + corners[3][0] * 0.3, front_center[1] * 0.7 + corners[3][1] * 0.3),
            (front_center[0] * 0.7 + corners[2][0] * 0.3, front_center[1] * 0.7 + corners[2][1] * 0.3),
            (mid_right[0], mid_right[1]),
            (mid_left[0], mid_left[1]),
        ]
        pygame.draw.polygon(screen, self.color_window, window_points)
        
        # Draw headlights
        if abs(self.velocity) > 0.5:  # Only when moving
            theta = np.radians(self.angle)
            
            # Left headlight
            light_left = (
                corners[3][0] + 8 * np.cos(theta),
                corners[3][1] + 8 * np.sin(theta)
            )
            # Right headlight
            light_right = (
                corners[2][0] + 8 * np.cos(theta),
                corners[2][1] + 8 * np.sin(theta)
            )
            
            if config.ENABLE_GLOW:
                # Draw glow effect
                for radius in [8, 6, 4]:
                    alpha = 60 if radius == 8 else 120 if radius == 6 else 180
                    glow_surf = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
                    glow_color = (*self.color_light, alpha)
                    pygame.draw.circle(glow_surf, glow_color, (radius, radius), radius)
                    screen.blit(glow_surf, (light_left[0] - radius, light_left[1] - radius))
                    screen.blit(glow_surf, (light_right[0] - radius, light_right[1] - radius))
            
            # Draw headlight centers
            pygame.draw.circle(screen, self.color_light, (int(light_left[0]), int(light_left[1])), 3)
            pygame.draw.circle(screen, self.color_light, (int(light_right[0]), int(light_right[1])), 3)
        
        # Draw wheels
        wheel_positions = [
            corners[0],  # Rear left
            corners[1],  # Rear right
            corners[2],  # Front right
            corners[3],  # Front left
        ]
        
        for i, pos in enumerate(wheel_positions):
            # Larger wheels for better visibility
            pygame.draw.circle(screen, self.color_wheel, (int(pos[0]), int(pos[1])), 7)
            pygame.draw.circle(screen, (20, 20, 20), (int(pos[0]), int(pos[1])), 4)
            
        # Draw speedometer indicator on car (small speed bar)
        if abs(self.velocity) > 0.1:
            speed_ratio = abs(self.velocity) / self.max_speed
            bar_length = int(self.length * 0.3 * speed_ratio)
            
            rear_center = ((corners[0][0] + corners[1][0]) / 2, (corners[0][1] + corners[1][1]) / 2)
            theta = np.radians(self.angle)
            
            bar_end = (
                rear_center[0] - bar_length * np.cos(theta),
                rear_center[1] - bar_length * np.sin(theta)
            )
            
            speed_color = (46, 204, 113) if self.velocity > 0 else (231, 76, 60)
            pygame.draw.line(screen, speed_color, rear_center, bar_end, 3)
            
    # def get_info(self):
    #     """Get current car state information"""
    #     return {
    #         'position': (self.x, self.y),
    #         'angle': self.angle,
    #         'velocity': self.velocity,
    #         'steering': self.steering_angle,
    #         'particles': len(self.particles)
    #     }
    def get_info(self):
        """Get current car state information"""
        return {
            'position': (self.x, self.y),
            'angle': self.angle,
            'velocity': self.velocity,
            'steering': self.steering_angle,
            'left_wheel': self.left_wheel_velocity,
            'right_wheel': self.right_wheel_velocity,
            'particles': len(self.particles)
        }
